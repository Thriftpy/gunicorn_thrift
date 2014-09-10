# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

try:
    import thriftpy
except ImportError:
    raise RuntimeError("You need thrift installed to use this worker.")

from thriftpy.transport import TSocket
from thriftpy.transport import TTransportException

from gunicorn.workers.sync import SyncWorker
from gunicorn.workers.ggevent import GeventWorker
from gunicorn.errors import AppImportError


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


class SyncThriftPyWorker(SyncWorker):
    def run(self):
        check_protocol_and_transport(self.app)
        super(SyncThriftPyWorker, self).run()

    def handle(self, listener, client, addr):
        if self.app.cfg.thrift_client_timeout is not None:
            client.settimeout(self.app.cfg.thrift_client_timeout)

        result = TSocket()
        result.set_handle(client)

        try:
            itrans = self.app.tfactory.get_transport(result)
            otrans = self.app.tfactory.get_transport(result)
            iprot = self.app.pfactory.get_protocol(itrans)
            oprot = self.app.pfactory.get_protocol(otrans)

            try:
                while True:
                    self.app.thrift_app.process(iprot, oprot)
                    self.notify()
            except TTransportException:
                pass
        except Exception as e:
            logging.exception(e)
        finally:
            itrans.close()
            otrans.close()

    def handle_exit(self, sig, frame):
        ret = super(SyncThriftPyWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret


class GeventThriftPyWorker(GeventWorker):
    def run(self):
        check_protocol_and_transport(self.app)
        super(GeventThriftPyWorker, self).run()

    def handle(self, listener, client, addr):
        if self.app.cfg.thrift_client_timeout is not None:
            client.settimeout(self.app.cfg.thrift_client_timeout)

        result = TSocket()
        result.set_handle(client)

        try:
            itrans = self.app.tfactory.get_transport(result)
            otrans = self.app.tfactory.get_transport(result)
            iprot = self.app.pfactory.get_protocol(itrans)
            oprot = self.app.pfactory.get_protocol(otrans)

            try:
                while True:
                    self.app.thrift_app.process(iprot, oprot)
            except TTransportException:
                pass
        except Exception as e:
            logger.exception(e)
        finally:
            itrans.close()
            otrans.close()

    def handle_exit(self, sig, frame):
        ret = super(GeventThriftPyWorker, self).handle_exit(sig, frame)
        self.cfg.worker_term(self)
        return ret
