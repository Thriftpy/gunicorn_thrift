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

Parameter: `-k`, `--worker-class`  
Config file: `worker_class`  
Default: `thrift_sync`

There are 4 types of workers avaiable.

* `thrift_sync`: sync worker.
* `thrift_gevent`: gevent worker.
* `thriftpy_sync`: sync worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)
* `thriftpy_gevent`: gevent worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)

note: If you wants to use `thriftpy_sync` or `thriftpy_gevent`, make sure the following:

* Version of `thriftpy` should be higher than `0.1.10`.
* `--thrift-protocol-factory` should be set to either `thriftpy.protocol:TCyBinaryProtocolFactory` or `thriftpy.protocol:TBinaryProtocolFactory`
* `--thrift-transport-factory` should be set to either `thriftpy.transport:TCyBufferedTransportFactory` or `thriftpy.transport:TBufferedTransportFactory`


### Transport factory

The transport factory to use for handling connections.

Parameter: `--thrift-transport-factory`  
Config file: `thrift_transport_factory`  
Default: `thrift.transport.TTransport:TBufferedTransportFactory`


### Protocol factory

The protocol factory to use for parsing requests.

Parameter: `--thrift-protocol-factory`  
Config file: `thrift_protocol_factory`  
Default: `thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory`

### Client timeout

Seconds to timeout a client if it is silent after this duration.

Parameter: `--thrift-client-timeout`  
Config file: `thrift_client_timeout`  
Default: `None` (Never time out a client)
