# -*- coding: utf-8 -

import os
import sys

from gunicorn.app.base import Application
import gunicorn.workers

# `config` is unused in this module but must be imported to register config
# options with gunicorn
from . import config
from . import utils
from .six import AVAILABLE_WORKERS

# register thrift workers

gunicorn.workers.SUPPORTED_WORKERS.update(AVAILABLE_WORKERS)


class ThriftApplication(Application):
    def init(self, parser, opts, args):
        if len(args) != 1:
            parser.error("No application name specified.")
        self.cfg.set("default_proc_name", args[0])

        self.app_uri = args[0]

        if opts.worker_class and \
                opts.worker_class not in AVAILABLE_WORKERS:
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

    def run(self):
        if self.cfg.service_register_cls:
            service_register_cls = utils.load_obj(
                self.cfg.service_register_cls)
            self.service_watcher = service_register_cls(
                self.cfg.service_register_conf, self)
            # generate the instances to register
            instances = []
            for i in self.cfg.address:
                port = i[1]
                instances.append({'port': {"main": port},
                                  'meta': None,
                                  'state': 'up'})
            self.service_watcher.register_instances(instances)
        super(ThriftApplication, self).run()


def run():
    from gunicorn_thrift.thriftapp import ThriftApplication
    ThriftApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
