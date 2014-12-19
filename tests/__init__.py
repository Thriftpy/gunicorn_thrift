import sys

import pytest


requires_py27 = pytest.mark.skipif(sys.version_info[:2] != (2, 7),
                                   reason='requires py27')


class AboutToShutDownException(Exception):
    pass


def make_client(service_cls, host='127.0.0.1', port=8000):
    import thriftpy.rpc
    return thriftpy.rpc.make_client(service_cls, host, port)
