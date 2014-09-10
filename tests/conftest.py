#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import time
import pytest
import subprocess


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


@pytest.fixture(scope="session")
def pingpong_thrift_server(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.app:app", "-c", "tests/gunicorn_config.py"],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture(scope="session")
def timeout_pingpong_thrift_server(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.app:app", "-c",
            "tests/gunicorn_timeout_config.py"],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def shutdown():
        os.kill(gunicorn_server.pid, signal.SIGTERM)

    request.addfinalizer(shutdown)
    time.sleep(1)

    return gunicorn_server


@pytest.fixture
def volatile_pingpong_thrift_server(request, make_test_thrift):
    gunicorn_server = subprocess.Popen(
        ["gunicorn_thrift", "tests.app:app", "-c", "tests/gunicorn_config.py",
            "--bind", "0.0.0.0:8004"],
        stdin=subprocess.PIPE, stderr=subprocess.PIPE
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
