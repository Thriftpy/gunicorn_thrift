# -*- coding: utf-8 -*-

import os
import importlib
from gunicorn.errors import AppImportError


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


def check_protocol_and_transport_for_thriftpy_woker(cfg):
    if not cfg.thrift_protocol_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use protocol from thriftpy,'
            'specify `thrift_protocol_factory` as one of the '
            'following:'
            '`thriftpy2.protocol:TCyBinaryProtocolFactory`, '
            '`thriftpy2.protocol:TBinaryProtocolFactory`'
            )

    if not cfg.thrift_transport_factory.startswith('thriftpy'):
        raise AppImportError(
            'Thriftpy worker can only use transport from thriftpy,'
            'specify `thrift_transport_factory` as one of the '
            'following:'
            '`thriftpy2.transport:TCyBufferedTransportFactory`, '
            '`thriftpy2.transport:TBufferedTransportFactory`'
            )
