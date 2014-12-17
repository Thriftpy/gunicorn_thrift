# -*- coding: utf-8 -*-


from gunicorn import six
from gunicorn.config import Setting, validate_string, validate_pos_int,\
    WorkerClass, validate_callable

from .six import DEFAULT_WORKER, DEFAULT_TRANSPORT, DEFAULT_PROTOCOL


WorkerClass.default = DEFAULT_WORKER


class ThriftTransportFactoryClass(Setting):
    name = "thrift_transport_factory"
    section = "Thrift"
    cli = ["--thrift-transport-factory"]
    validator = validate_string
    default = DEFAULT_TRANSPORT
    desc = """\
        The factory class for thrift transport.
    """


class ThriftProtocolFactoryClass(Setting):
    name = "thrift_protocol_factory"
    section = "Thrift"
    cli = ["--thrift-protocol-factory"]
    validator = validate_string
    default = DEFAULT_PROTOCOL
    desc = """\
        The factory class for thrift transport.
    """


class ThriftClientTimeout(Setting):
    name = "thrift_client_timeout"
    section = "Thrift"
    cli = ["--thrift-client-timeout"]
    validator = validate_pos_int
    default = None
    desc = """\
        Seconds to timeout a client if client is silent after this duration
    """


class WorkerTerm(Setting):
    name = "worker_term"
    section = "Server Hooks"
    validator = validate_callable(1)
    type = six.callable

    def worker_term(worker):
        pass

    default = staticmethod(worker_term)
    desc = """\
        Called just after a worker received SIGTERM, and about to gracefully
        shutdown.

        The callable needs to accept one instance variable for the initialized
        Worker.
        """


class ClientConnected(Setting):
    name = "on_connected"
    section = "Server Hooks"
    validator = validate_callable(2)
    type = six.callable

    def on_connected(worker, addr):
        pass

    default = staticmethod(on_connected)
    desc = """\
        Called just after a connection is made.

        The callable needs to accept two instance variable for the worker and
        the connected client address.
        """
