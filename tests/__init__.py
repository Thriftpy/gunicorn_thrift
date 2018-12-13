import sys


class AboutToShutDownException(Exception):
    pass


def make_client(service_cls, host='127.0.0.1', port=8000):
    import thriftpy2.rpc
    return thriftpy2.rpc.make_client(service_cls, host, port)
