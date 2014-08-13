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


class SyncThriftPyWorker(SyncWorker):
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
