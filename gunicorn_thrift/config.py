# -*- coding: utf-8 -*-


from gunicorn.config import Setting, validate_string, validate_pos_int


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
    default = \
        "thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory"
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
