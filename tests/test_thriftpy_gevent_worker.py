# -*- coding: utf-8 -*-


import os
import signal
import time

import pytest
from thriftpy.transport import TTransportException

from . import AboutToShutDownException, make_client
from .six import requires_py27


@requires_py27
class TestThriftpyGeventWorker:
    def test_connectivity(self, PingServiceThriftpy,
                          pingpong_thriftpy_server_gevent):
        server = make_client(PingServiceThriftpy)
        assert 'pong' == server.ping()

    def test_client_timeout(self, PingServiceThriftpy,
                            timeout_pingpong_thriftpy_server_gevent,
                            TSocket, TTransport, TBinaryProtocol):
        server = make_client(PingServiceThriftpy, port=8002)
        time.sleep(2)
        with pytest.raises(TTransportException):
            assert 'pong' == server.ping()

    @pytest.mark.xfail
    def test_server_disconnect_connection_when_gracefully_stopping(
            self, PingServiceThriftpy,
            volatile_pingpong_thriftpy_server_gevent):
        server = make_client(PingServiceThriftpy, port=8004)
        assert 'pong' == server.ping()

        # restart
        os.kill(volatile_pingpong_thriftpy_server_gevent.pid, signal.SIGHUP)
        time.sleep(1)
        with pytest.raises(AboutToShutDownException):
            server.ping()

        # Try again for new worker
        server = make_client(PingServiceThriftpy, port=8004)
        assert 'pong' == server.ping()
