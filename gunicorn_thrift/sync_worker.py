# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

try:
    import thrift
except ImportError:
    raise RuntimeError("You need thrift installed to use this worker.")

from thrift.transport import TSocket
from thrift.transport import TTransport

from gunicorn.workers.sync import SyncWorker


class SyncThriftWorker(SyncWorker):
    def handle_request(self, client):
        try:
            itrans = self.wsgi.tfactory.getTransport(client)
            otrans = self.wsgi.tfactory.getTransport(client)
            iprot = self.wsgi.pfactory.getProtocol(itrans)
            oprot = self.wsgi.pfactory.getProtocol(otrans)

            try:
                while True:
                    self.processor.process(iprot, oprot)
            except TTransport.TTransportException:
                pass
        except Exception as e:
            logging.exception(e)
        finally:
            itrans.close()
            otrans.close()

    def handle(self, client):
        result = TSocket()
        result.setHandle(client)

        try:
            itrans = self.inputTransportFactory.getTransport(client)
            otrans = self.outputTransportFactory.getTransport(client)
            iprot = self.inputProtocolFactory.getProtocol(itrans)
            oprot = self.outputProtocolFactory.getProtocol(otrans)

            try:
                while True:
                    self.processor.process(iprot, oprot)
            except TTransport.TTransportException:
                pass
        except Exception as e:
            logging.exception(e)
        finally:
            itrans.close()
            otrans.close()
