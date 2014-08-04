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
    def handle(self, listener, client, addr):
        result = TSocket.TSocket()
        result.setHandle(client)

        try:
            itrans = self.app.tfactory.getTransport(result)
            otrans = self.app.tfactory.getTransport(result)
            iprot = self.app.pfactory.getProtocol(itrans)
            oprot = self.app.pfactory.getProtocol(otrans)

            try:
                while True:
                    self.app.thrift_app.process(iprot, oprot)
            except TTransport.TTransportException:
                pass
        except Exception as e:
            logging.exception(e)
        finally:
            itrans.close()
            otrans.close()
