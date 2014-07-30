# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.


from gunicorn.app.base import Application
from gunicorn import util

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class ThriftApplication(Application):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No application name specified.")
        self.cfg.set("default_proc_name", args[0])

        self.app_uri = args[0]
        self.thrift_processor = args

        self.tfactory = TTransport.TBufferedTransportFactory()
        self.pfactory = TBinaryProtocol.TBinaryProtocolAcceleratedFactory()
        self.cfg.set(
            "worker_class", "gunicorn_thrift.sync_worker.SyncThriftWorker"
            )

    def load(self):
        self.chdir()
        return util.import_app(self.app_uri)


def run():
    from gunicorn_thrift.app import ThriftApplication
    ThriftApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
