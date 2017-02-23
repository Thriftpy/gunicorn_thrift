# -*- coding: utf-8 -*-

import os
import importlib
from gunicorn.errors import AppImportError

import socket
import struct
import fcntl


def get_IPv4(ethname):
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0X8915,
        struct.pack('256s', ethname[:15])
        )[20:24])
    return ip


def load_obj(import_path):
    parts = import_path.split(":", 1)
    if len(parts) == 1:
        raise ValueError("Wrong import path, module:obj please")

    module, obj = parts[0], parts[1]

    try:
        mod = importlib.import_module(module)
    except ImportError:
        if module.endswith(".py") and os.path.exists(module):
            raise ImportError(
                "Failed to find application, did "
                "you mean '%s:%s'?" % (module.rsplit(".", 1)[0], obj)
                )
        else:
            raise

    try:
        app = getattr(mod, obj)
    except AttributeError:
        raise AppImportError("Failed to find application object: %r" % obj)

    return app


class ProcessorMixin(object):
    def get_thrift_processor(self):
        return self.app.thrift_app.get_processor() if \
            self.app.cfg.thrift_processor_as_factory else \
            self.app.thrift_app
