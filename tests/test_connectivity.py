# -*- coding: utf-8 -*-

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def test_connectivity(pingpong_thrift_server):
    from pingpong_sdk.pingpong import PingService
    transport = TSocket.TSocket('localhost', 8000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    assert 'pong' == server.ping()
    transport.close()

if __name__ == '__main__':
    test_connectivity(None)
