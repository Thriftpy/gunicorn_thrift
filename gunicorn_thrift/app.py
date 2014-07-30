# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.


import os
import sys

from gunicorn.errors import AppImportError
from gunicorn.app.base import Application

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class ThriftApplication(Application):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No application name specified.")
        self.cfg.set("default_proc_name", args[0])

        self.app_uri = args[0]

        self.tfactory = TTransport.TBufferedTransportFactory()
        self.pfactory = TBinaryProtocol.TBinaryProtocolAcceleratedFactory()

        self.cfg.set("worker_class", "thrift_sync")

    def load_thrift_app(self):
        parts = self.app_uri.split(":", 1)
        if len(parts) == 1:
            module, obj = self.app_uri, "application"
        else:
            module, obj = parts[0], parts[1]

        try:
            __import__(module)
        except ImportError:
            if module.endswith(".py") and os.path.exists(module):
                raise ImportError(
                    "Failed to find application, did "
                    "you mean '%s:%s'?" % (module.rsplit(".", 1)[0], obj)
                    )
            else:
                raise

        mod = sys.modules[module]

        try:
            app = eval(obj, mod.__dict__)
        except NameError:
            raise AppImportError("Failed to find application: %r" % module)

        if app is None:
            raise AppImportError("Failed to find application object: %r" % obj)

        return app

    def load(self):
        self.chdir()
        self.thrift_handler = self.load_thrift_app()
        return lambda: 1

    def chdir(self):
        os.chdir(self.cfg.chdir)
        sys.path.insert(0, self.cfg.chdir)


def run():
    from gunicorn_thrift.app import ThriftApplication
    ThriftApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
