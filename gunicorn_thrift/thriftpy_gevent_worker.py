# -*- coding: utf-8 -*-


import errno
import socket
import logging

try:
    import gevent
except RuntimeError:
    raise RuntimeError('`thriftpy_gevent` worker is unavailable because '
                       'gevent is not installed')

try:
    import thriftpy
except ImportError:
    raise RuntimeError('`thriftpy_gevent` worker is unavailable because '
                       'thriftpy is not installed')


from thriftpy.transport import TSocket
from thriftpy.transport import TTransportException
from thriftpy.protocol.exc import TProtocolException
from thriftpy.protocol.cybin import ProtocolError

from gunicorn.errors import AppImportError
from gunicorn.workers.ggevent import GeventWorker

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


class GeventThriftPyWorker(GeventWorker, ProcessorMixin):
    def run(self):
        check_protocol_and_transport(self.app)
        super(GeventThriftPyWorker, self).run()

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
                    processor.process(iprot, oprot)
            except TTransportException:
                pass
        except (TProtocolException, ProtocolError) as err:
            self.log.warning(
                "Protocol error, is client(%s) correct? %s", addr, err
                )
        except socket.timeout:
            self.log.warning('Client timeout: %r', addr)
        except socket.error as e:
            if e.args[0] == errno.ECONNRESET:
                self.log.debug('%r: %r', addr, e)
            elif e.args[0] == errno.EPIPE:
                self.log.warning('%r: %r', addr, e)
            else:
                self.log.exception('%r: %r', addr, e)
        except Exception as e:
            self.log.exception('%r: %r', addr, e)
        finally:
            itrans.close()
            otrans.close()
            self.cfg.post_connect_closed(self)

    def handle_exit(self, sig, frame):
        ret = super(GeventThriftPyWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret
