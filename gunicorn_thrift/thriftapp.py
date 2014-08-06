# -*- coding: utf-8 -

import os
import sys

import utils

from gunicorn.app.base import Application

# register thrift specific options
import config

# register thrift workers
import gunicorn.workers

AVAILABLE_THRIFT_WORKERS = {
    'thrift_sync': 'gunicorn_thrift.sync_worker.SyncThriftWorker',
    'thrift_gevent': 'gunicorn_thrift.gevent_worker.GeventThriftWorker',
    'thriftpy_sync': 'gunicorn_thrift.sync_worker.SyncThriftPyWorker',
    'thriftpy_gevent': 'gunicorn_thrift.gevent_worker.GeventThriftPyWorker',
    }

gunicorn.workers.SUPPORTED_WORKERS.update(AVAILABLE_THRIFT_WORKERS)


class ThriftApplication(Application):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No application name specified.")
        self.cfg.set("default_proc_name", args[0])

        self.app_uri = args[0]

        if opts.worker_class and \
                opts.worker_class not in AVAILABLE_THRIFT_WORKERS:
            raise ValueError

    def load_thrift_app(self):
        return utils.load_obj(self.app_uri)

    def load(self):
        self.chdir()
        self.tfactory = utils.load_obj(self.cfg.thrift_transport_factory)()
        self.pfactory = utils.load_obj(self.cfg.thrift_protocol_factory)()
        self.thrift_app = self.load_thrift_app()
        return lambda: 1

    def chdir(self):
        os.chdir(self.cfg.chdir)
        sys.path.insert(0, self.cfg.chdir)


def run():
    from gunicorn_thrift.thriftapp import ThriftApplication
    ThriftApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
