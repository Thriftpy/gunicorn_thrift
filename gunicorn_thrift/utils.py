# -*- coding: utf-8 -*-

import os
import sys
from gunicorn.errors import AppImportError


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
