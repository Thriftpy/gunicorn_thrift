# -*- coding: utf-8 -*-

import errno
import socket
import logging

try:
    import thriftpy
except ImportError:
    raise RuntimeError('`thriftpy_sync` worker is unavailable because '
                       'thriftpy is not installed')

from thriftpy.transport import TSocket
from thriftpy.transport import TTransportException

from gunicorn.errors import AppImportError
from gunicorn.workers.sync import SyncWorker

from .utils import ProcessorMixin

logger = logging.getLogger(__name__)


def check_protocol_and_transport(app):
    if not app.cfg.thrift_protocol_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use protocol from thriftpy,'
            'specify `thrift_protocol_factory` as one of the '
            'following:'
            '`thriftpy.protocol:TCyBinaryProtocolFactory`, '
            '`thriftpy.protocol:TBinaryProtocolFactory`'
            )

    if not app.cfg.thrift_transport_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use transport from thriftpy,'
            'specify `thrift_transport_factory` as one of the '
            'following:'
            '`thriftpy.transport:TCyBufferedTransportFactory`, '
            '`thriftpy.transport:TBufferedTransportFactory`'
            )


class SyncThriftPyWorker(SyncWorker, ProcessorMixin):
    def run(self):
        check_protocol_and_transport(self.app)
        super(SyncThriftPyWorker, self).run()

    def handle(self, listener, client, addr):
        self.cfg.on_connected(self, addr)
        if self.app.cfg.thrift_client_timeout is not None:
            client.settimeout(self.app.cfg.thrift_client_timeout)

        result = TSocket()
        result.set_handle(client)

        try:
            itrans = self.app.tfactory.get_transport(result)
            otrans = self.app.tfactory.get_transport(result)
            iprot = self.app.pfactory.get_protocol(itrans)
            oprot = self.app.pfactory.get_protocol(otrans)

            processor = self.get_thrift_processor()

            try:
                while True:
                    self.nr += 1
                    if self.alive and self.nr >= self.max_requests:
                        self.log.info("Autorestarting worker after current process.")
                        self.alive = False                    
                    processor.process(iprot, oprot)
                    self.notify()
            except TTransportException:
                pass
        except socket.error as e:
            if e.args[0] == errno.ECONNRESET:
                self.log.debug(e)
            else:
                self.log.exception(e)
        except Exception as e:
            self.log.exception(e)
        finally:
            itrans.close()
            otrans.close()
            self.cfg.post_connect_closed(self)

    def handle_exit(self, sig, frame):
        ret = super(SyncThriftPyWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret
