#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import time
import pytest
import subprocess


@pytest.fixture(scope="session")
def TSocket():
    from thrift.transport import TSocket as _TSocket
    return _TSocket


@pytest.fixture(scope="session")
def TTransport():
    from thrift.transport import TTransport as _TTransport
    return _TTransport


@pytest.fixture(scope="session")
def TBinaryProtocol():
    from thrift.protocol import TBinaryProtocol as _TBinaryProtocol
    return _TBinaryProtocol


@pytest.fixture(scope="session")
def make_test_thrift(request):
    try:
        os.mkdir("tests/pingpong_sdk")
    except (IOError, OSError):
        pass
    exit_status = subprocess.call(
        "thrift --out tests/pingpong_sdk --gen "
        "py:new_style,utf8strings tests/pingpong.thrift".split()
        )
    if exit_status:
        raise RuntimeError("thrift generation failed")

    def rm():
        subprocess.call(['rm', '-rf', 'pingpong_sdk'])

    request.addfinalizer(rm)


#
# sync worker fixtures
#
@pytest.fixture(scope="session")
def pingpong_thrift_server_sync(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_config.py", "-k", "thrift_sync"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture(scope="session")
def timeout_pingpong_thrift_server_sync(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_timeout_config.py", "-k", "thrift_sync"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def volatile_pingpong_thrift_server_sync(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_config.py", "--bind", "0.0.0.0:8004", "-k",
         "thrift_sync"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


#
# gevent worker fixtures
#
@pytest.fixture(scope="session")
def pingpong_thrift_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_config.py", "-k", "thrift_gevent"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture(scope="session")
def timeout_pingpong_thrift_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_timeout_config.py", "-k", "thrift_gevent"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def volatile_pingpong_thrift_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thrift_app:app", "-c",
         "tests/gunicorn_config.py", "--bind", "0.0.0.0:8004", "-k",
         "thrift_gevent"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


#
# thriftpy sync worker fixtures
#
@pytest.fixture(scope="session")
def pingpong_thriftpy_server_sync(request):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_config.py", "-k", "thriftpy_sync",
         "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory",
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture(scope="session")
def timeout_pingpong_thriftpy_server_sync(request):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_timeout_config.py", "-k", "thriftpy_sync",
         "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory",
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def volatile_pingpong_thriftpy_server_sync(request):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_config.py", "--bind", "0.0.0.0:8004", "-k",
         "thriftpy_sync", "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory"
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


#
# thriftpy gevent worker fixtures
#
@pytest.fixture(scope="session")
def pingpong_thriftpy_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_config.py", "-k", "thriftpy_gevent",
         "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory",
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture(scope="session")
def timeout_pingpong_thriftpy_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_timeout_config.py", "-k", "thriftpy_gevent",
         "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory",
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def volatile_pingpong_thriftpy_server_gevent(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.thriftpy_app:app", "-c",
         "tests/gunicorn_config.py", "--bind", "0.0.0.0:8004", "-k",
         "thriftpy_gevent", "--thrift-protocol-factory",
         "thriftpy.protocol:TBinaryProtocolFactory",
         "--thrift-transport-factory",
         "thriftpy.transport:TBufferedTransportFactory",
         "--log-file", "-"],
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def PingService(make_test_thrift):
    from pingpong_sdk.pingpong import PingService
    return PingService


@pytest.fixture
def PingServiceThriftpy(make_test_thrift):
    import thriftpy
    pingpong_thrift = thriftpy.load("tests/pingpong.thrift")
    return pingpong_thrift.PingService
