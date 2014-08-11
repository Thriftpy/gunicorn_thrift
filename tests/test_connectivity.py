# -*- coding: utf-8 -*-

import time

import os
import signal
import pytest

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from pingpong_sdk.pingpong import PingService


def test_connectivity(pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    assert 'pong' == server.ping()
    transport.close()


def test_client_timeout(timeout_pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8002)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    time.sleep(2)
    with pytest.raises(TSocket.TTransportException):
        assert 'pong' == server.ping()
        transport.close()


def test_server_disconnect_connection_when_gracefully_stopping(
        volatile_pingpong_thrift_server):
    transport = TSocket.TSocket('localhost', 8004)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    assert 'pong' == server.ping()

    os.kill(volatile_pingpong_thrift_server.pid, signal.SIGHUP)  # restart
    time.sleep(1)
    with pytest.raises(PingService.AboutToShutDownException):
        server.ping()
    transport.close()

    # Try again for new worker
    transport = TSocket.TSocket('localhost', 8004)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    assert 'pong' == server.ping()

if __name__ == '__main__':
    test_connectivity(None)
