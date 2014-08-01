# -*- coding: utf-8 -

import os
import sys

from gunicorn.errors import AppImportError
from gunicorn.app.base import Application

# register thrift specific options
import config

# register thrift workers
import gunicorn.workers
gunicorn.workers.SUPPORTED_WORKERS.update({
    'thrift_sync': 'gunicorn_thrift.sync_worker.SyncThriftWorker',
    })


def load_obj(import_path):
    parts = import_path.split(":", 1)
    if len(parts) == 1:
        raise ValueError("Wrong import path, module:obj please")

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


class ThriftApplication(Application):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No application name specified.")
        self.cfg.set("default_proc_name", args[0])

        self.app_uri = args[0]

        self.tfactory = load_obj(self.cfg.thrift_transport_factory)()
        self.pfactory = load_obj(self.cfg.thrift_protocol_factory)()
        self.cfg.set("worker_class", self.cfg.thrift_worker)

    def load_thrift_app(self):
        return load_obj(self.app_uri)

    def load(self):
        self.chdir()
        self.thrift_handler = self.load_thrift_app()
        return lambda: 1

    def chdir(self):
        os.chdir(self.cfg.chdir)
        sys.path.insert(0, self.cfg.chdir)


def run():
    from gunicorn_thrift.thriftapp import ThriftApplication
    ThriftApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
