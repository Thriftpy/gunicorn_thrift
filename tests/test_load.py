#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import time

import gevent
import gevent.monkey
gevent.monkey.patch_all()

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def assert_ping():
    from pingpong_sdk.pingpong import PingService
    transport = TSocket.TSocket('localhost', 8000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
    transport.open()
    server = PingService.Client(protocol)
    assert 'pong' == server.ping()
    transport.close()


def test_one_worker(pingpong_thrift_server):
    for i in range(9999):
        assert_ping()


def test_two_worker(pingpong_thrift_server):
    rounds = 9999
    os.kill(pingpong_thrift_server.pid, signal.SIGTTIN)
    begin = time.time()
    jobs = [gevent.spawn(assert_ping) for i in range(rounds)]
    gevent.joinall(jobs, raise_error=True)
    end = time.time()

    print("Total time of %s calls:" % rounds, end - begin)
