# -*- coding: utf-8 -*-

import errno
import socket
import logging

try:
    import thriftpy2
except ImportError:
    raise RuntimeError('`thriftpy_sync` worker is unavailable because '
                       'thriftpy2 is not installed')

from thriftpy2.transport import TSocket
from thriftpy2.transport import TTransportException
from thriftpy2.thrift import TDecodeException

from gunicorn.errors import AppImportError
from gunicorn.workers.sync import SyncWorker

from .utils import ProcessorMixin

logger = logging.getLogger(__name__)


def check_protocol_and_transport(app):
    if not app.cfg.thrift_protocol_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use protocol from thriftpy2,'
            'specify `thrift_protocol_factory` as one of the '
            'following:'
            '`thriftpy2.protocol:TCyBinaryProtocolFactory`, '
            '`thriftpy2.protocol:TBinaryProtocolFactory`'
            )

    if not app.cfg.thrift_transport_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use transport from thriftpy2,'
            'specify `thrift_transport_factory` as one of the '
            'following:'
            '`thriftpy2.transport:TCyBufferedTransportFactory`, '
            '`thriftpy2.transport:TBufferedTransportFactory`'
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
                    processor.process(iprot, oprot)
                    self.notify()
            except TTransportException:
                pass
        except TDecodeException as err:
            self.log.exception('%r: %r', addr, err)
            self.cfg.on_tdecode_exception(err)
        except socket.timeout:
            self.log.warning('Client timeout: %r', addr)
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
