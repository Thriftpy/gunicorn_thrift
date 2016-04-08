# -*- coding: utf-8 -*-

import sys

PY_VERSION = sys.version_info[:3]


if PY_VERSION <= (2, 8, 0):
    DEFAULT_WORKER = "thrift_sync"
    DEFAULT_TRANSPORT = "thrift.transport.TTransport:TBufferedTransportFactory"
    DEFAULT_PROTOCOL = \
        "thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory"
    AVAILABLE_WORKERS = {
        'thrift_sync': 'gunicorn_thrift.sync_worker.SyncThriftWorker',
        'thrift_gevent': 'gunicorn_thrift.gevent_worker.GeventThriftWorker',
        'thriftpy_sync': 'gunicorn_thrift.thriftpy_sync_worker.SyncThriftPyWorker',
        'thriftpy_gevent': 'gunicorn_thrift.thriftpy_gevent_worker.GeventThriftPyWorker',
        }
else:
    DEFAULT_WORKER = "thriftpy_sync"
    DEFAULT_TRANSPORT = "thriftpy.transport:TBufferedTransportFactory"
    DEFAULT_PROTOCOL = "thriftpy.protocol:TBinaryProtocolFactory"
    AVAILABLE_WORKERS = {
        'thriftpy_sync': 'gunicorn_thrift.thriftpy_sync_worker.SyncThriftPyWorker',
        'thriftpy_gevent': 'gunicorn_thrift.thriftpy_gevent_worker.GeventThriftPyWorker',
        }
