gunicorn_thrift
===============

[![Build Status](https://travis-ci.org/eleme/gunicorn_thrift.svg?branch=master)](https://travis-ci.org/eleme/gunicorn_thrift)

Thrift app and worker for gunicorn!

## Why?

* graceful reload/shutdown.
* manage worker number at runtime.
* and everything else `gunicorn` has to offer.

## Examples

1. Generate thrift files:
    ```bash
    % thrift --out tests/pingpong_sdk --gen py:new_style,utf8strings tests/pingpong.thrift
    ```

2. Write thrift app.
    ```python
    #! /usr/bin/env python
    # tests/app.py
    # -*- coding: utf-8 -*-
    
    import os
    from pingpong_sdk.pingpong import PingService
    
    class PingpongServer(object):
        def ping(self):
            return "pong"
    
    app = PingService.Processor(PingpongServer())
    ```

3. Fire up app.
    ```bash
    % gunicorn_thrift tests.app:app -k thrift_sync
    % gunicorn_thrift tests.app:app -k thrift_gevent
    ```

## Configs

### Workers

There are 4 types of workers avaiable.

* `thrift_sync`: sync worker.
* `thrift_gevent`: gevent worker.
* `thriftpy_sync`: sync worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)
* `thriftpy_gevent`: gevent worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)

### Transport factory

The transport factory to use for handling connections.

default: `thrift.transport.TTransport:TBufferedTransportFactory`


### Protocol factory

The protocol factory to use for parsing requests.

default: `thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory`

### Client timeout

Seconds to timeout a client if it is silent after this duration.

default: `None` (Never time out a client)
