# -*- coding: utf-8 -*-

import os
import signal
import time

import pytest

from .six import requires_py27


@requires_py27
class TestThriftSyncWorker:
    def test_connectivity(self, PingService,
                          pingpong_thrift_server_sync, TSocket, TTransport,
                          TBinaryProtocol):
        transport = TSocket.TSocket('localhost', 8000)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
        transport.open()
        server = PingService.Client(protocol)
        assert 'pong' == server.ping()
        transport.close()


    def test_client_timeout(self, PingService,
                            timeout_pingpong_thrift_server_sync,
                            TSocket, TTransport, TBinaryProtocol):
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
            self, PingService, volatile_pingpong_thrift_server_sync,
            TSocket, TTransport, TBinaryProtocol):
        transport = TSocket.TSocket('localhost', 8004)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
        transport.open()
        server = PingService.Client(protocol)
        assert 'pong' == server.ping()

        # restart
        os.kill(volatile_pingpong_thrift_server_sync.pid, signal.SIGHUP)
        time.sleep(1)
        with pytest.raises(PingService.AboutToShutDownException):
            server.ping()
        transport.close()

        # Try again for new worker
        time.sleep(1)
        transport = TSocket.TSocket('localhost', 8004)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
        transport.open()
        server = PingService.Client(protocol)
        assert 'pong' == server.ping()
