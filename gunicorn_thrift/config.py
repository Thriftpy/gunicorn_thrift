# -*- coding: utf-8 -*-


from gunicorn.config import Setting, validate_string


class ThriftTransportFactoryClass(Setting):
    name = "thrift_transport_factory"
    section = "Thrift"
    cli = ["--thrift-transport-factory"]
    validator = validate_string
    default = "thrift.transport.TTransport:TBufferedTransportFactory"
    desc = """\
        The factory class for thrift transport.
    """


class ThriftProtocolFactoryClass(Setting):
    name = "thrift_protocol_factory"
    section = "Thrift"
    cli = ["--thrift-protocol-factory"]
    validator = validate_string
    default = "thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory"
    desc = """\
        The factory class for thrift transport.
    """


class ThriftWorker(Setting):
    name = "thrift_worker"
    section = "Thrift"
    cli = ["--thrift-worker"]
    validator = validate_string
    default = "thrift_sync"
    desc = """\
        Worker class for thrift, this will overwrite worker option.
    """
