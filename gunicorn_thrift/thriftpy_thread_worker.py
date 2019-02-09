# -*- coding: utf-8 -*-

#
# This file is largely copied from gunicorn,
# which is released under the MIT license.
#

# The difference is that there's no default value for client timeout.
# If `thrift_client_timeout` is not provided, connection will be alive forever

import socket
import errno
import time

from functools import partial

from thriftpy2.transport import TSocket
from thriftpy2.transport import TTransportException
from thriftpy2.protocol.exc import TProtocolException
from thriftpy2.protocol.cybin import ProtocolError
from thriftpy2.thrift import TDecodeException

from gunicorn.workers.gthread import ThreadWorker, selectors, futures

from .utils import (
    ProcessorMixin,
    check_protocol_and_transport_for_thriftpy_woker,
    )


class TThreadClient(object):
    def __init__(self, app, client, addr, t_processor):
        self.app = app

        self.sock = client
        self.result = TSocket()
        self.result.set_handle(client)
        self.addr = addr

        self.t_processor = t_processor

        self.itrans = self.app.tfactory.get_transport(self.result)
        self.otrans = self.app.tfactory.get_transport(self.result)
        self.iprot = self.app.pfactory.get_protocol(self.itrans)
        self.oprot = self.app.pfactory.get_protocol(self.otrans)

        self.last_used = time.time()

        self.client_timeout = self.app.cfg.thrift_client_timeout

    def init(self):
        # flag the socket as blocked
        self.sock.setblocking(True)

    def close(self):
        self.result.close()

    def before_put_into_ioloop(self):
        # flag the socket as non blocked
        self.last_used = time.time()
        self.sock.setblocking(False)

    def is_expired(self):
        if self.client_timeout:
            return time.time() > self.client_timeout + self.last_used
        return False

    def process_single_rpc(self):
        keepalive = False
        try:
            self.t_processor.process(self.iprot, self.oprot)
            keepalive = True
        except TTransportException:
            pass
        except (TProtocolException, ProtocolError) as err:
            self.log.warning(
                "Protocol error, is client(%s) correct? %s", self.addr, err
                )
        except TDecodeException as err:
            self.log.exception('%r: %r', self.addr, err)
            self.app.cfg.on_tdecode_exception(err)
        except socket.timeout:
            self.log.warning('Client timeout: %r', self.addr)
        except socket.error as e:
            if e.args[0] == errno.ECONNRESET:
                self.log.debug('%r: %r', self.addr, e)
            elif e.args[0] == errno.EPIPE:
                self.log.warning('%r: %r', self.addr, e)
            else:
                self.log.exception('%r: %r', self.addr, e)
        except Exception as e:
            self.log.exception('%r: %r', self.addr, e)
        finally:
            if not keepalive:
                self.itrans.close()
                self.otrans.close()
                self.app.cfg.post_connect_closed(self)
            return (keepalive, self)


class ThriftpyThreadWorker(ThreadWorker, ProcessorMixin):
    def init_process(self):
        self.log.info("Starting thread worker, threads: %s", self.cfg.threads)
        return super(ThriftpyThreadWorker, self).init_process()

    @classmethod
    def check_config(cls, cfg, log):
        super(ThriftpyThreadWorker, cls).check_config(cfg, log)
        check_protocol_and_transport_for_thriftpy_woker(cfg)

    def accept(self, listener):
        try:
            client, addr = listener.accept()
            self.cfg.on_connected(self, addr)
            # initialize the connection object
            conn = TThreadClient(
                self.app, client, addr, self.get_thrift_processor()
                )
            self.nr += 1
            self.put_back_to_ioloop(conn)
        except socket.error as e:
            if e.args[0] not in (
                    errno.EAGAIN, errno.ECONNABORTED, errno.EWOULDBLOCK):
                raise

    def handle(self, conn):
        return conn.process_single_rpc()

    def handle_exit(self, sig, frame):
        ret = super(ThriftpyThreadWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret

    def put_back_to_ioloop(self, conn):
        conn.before_put_into_ioloop()

        with self._lock:
            self._keep.append(conn)

            # add the socket to the event loop
            self.poller.register(conn.sock, selectors.EVENT_READ,
                                 partial(self.reuse_connection, conn))

    def finish_request(self, fs):
        if fs.cancelled():
            fs.conn.close()
            return

        try:
            (keepalive, conn) = fs.result()
            # if the connection should be kept alived add it
            # to the eventloop and record it
            if keepalive:
                self.put_back_to_ioloop(conn)
            else:
                # remove the socket from the poller
                with self._lock:
                    try:
                        self.poller.unregister(conn.sock)
                    except socket.error as e:
                        if e.args[0] != errno.EBADF:
                            raise

                conn.close()
                self.nr -= 1
        except Exception:
            # an exception happened, make sure to close the
            # socket.
            self.nr -= 1
            fs.conn.close()

    def run(self):
        # Need to copy base method to add changes,
        # so that graceful restart can work

        # init listeners, add them to the event loop
        for s in self.sockets:
            s.setblocking(False)
            self.poller.register(s, selectors.EVENT_READ, self.accept)

        timeout = self.cfg.timeout or 0.5

        while self.alive:
            # notify the arbiter we are alive
            self.notify()

            # can we accept more connections?
            if self.nr < self.worker_connections:
                # wait for an event
                events = self.poller.select(0.02)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)

            if not self.is_parent_alive():
                break

            # hanle keepalive timeouts
            self.murder_keepalived()

            # if the number of connections is < to the max we can handle at
            # the same time there is no need to wait for one
            if len(self.futures) < self.cfg.threads:
                continue

            result = futures.wait(self.futures, timeout=timeout,
                                  return_when=futures.FIRST_COMPLETED)

            if not result.done:
                break
            else:
                [self.futures.remove(f) for f in result.done]

        # Added code for graceful restart
        try:
            # Closing listening sockets
            for s in self.sockets:
                s.close()

            # Handle current requests until graceful_timeout
            ts = time.time()
            while time.time() - ts <= self.cfg.graceful_timeout and self.nr:
                events = self.poller.select(0.02)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)
        except Exception:
            pass

        self.tpool.shutdown(False)
        self.poller.close()

    def murder_keepalived(self):
        while True:
            with self._lock:
                try:
                    # remove the connection from the queue
                    conn = self._keep.popleft()
                except IndexError:
                    break

            if conn.is_expired():
                self.nr -= 1
                # remove the socket from the poller
                with self._lock:
                    try:
                        self.poller.unregister(conn.sock)
                    except socket.error as e:
                        if e.args[0] != errno.EBADF:
                            raise

                # close the socket
                self.log.warning("Client timedout, closing: %s", conn.addr)
                conn.close()
            else:
                # add the connection back to the queue
                with self._lock:
                    self._keep.appendleft(conn)
                break
