# -*- coding: utf-8 -*-


from gunicorn.config import Setting, validate_string, KNOWN_SETTINGS


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
