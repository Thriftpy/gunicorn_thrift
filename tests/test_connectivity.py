# -*- coding: utf-8 -*-

import time

import os
import signal
import pytest

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def test_connectivity(PingService, pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    client = PingService.Client(protocol)
    assert 'pong' == client.ping()
    transport.close()


def test_client_timeout(PingService, timeout_pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8002)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    client = PingService.Client(protocol)
    time.sleep(2)
    with pytest.raises(TSocket.TTransportException):
        assert 'pong' == client.ping()
        transport.close()


def test_server_disconnect_connection_when_gracefully_stopping(
        PingService, volatile_pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8004)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    client = PingService.Client(protocol)
    assert 'pong' == client.ping()

    os.kill(volatile_pingpong_thrift_server.pid, signal.SIGHUP)  # restart
    time.sleep(1)
    with pytest.raises(PingService.AboutToShutDownException):
        client.ping()
    transport.close()

    # Try again for new worker
    transport = TSocket.TSocket('localhost', 8004)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    client = PingService.Client(protocol)
    assert 'pong' == client.ping()

if __name__ == '__main__':
    from pingpong_sdk.pingpong import PingService
    test_connectivity(PingService, None)
