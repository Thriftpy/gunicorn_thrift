gunicorn_thrift
===============

[![Build Status](https://travis-ci.org/eleme/gunicorn_thrift.svg?branch=master)](https://travis-ci.org/eleme/gunicorn_thrift)

Thrift app and worker for gunicorn!

## Why?

* graceful reload/shutdown.
* manage worker number at runtime.
* and everything else `gunicorn` has to offer.

## Supported Platforms

* Python 2.7, all worker classes
* Python 3.2+, `thriftpy_sync` worker class (neither gevent nor code generated
  using the Thrift toolkit are supported on Python 3)

## Examples

### Using `thrift`

1. Generate thrift files:
    ```bash
    % thrift --out tests/pingpong_sdk --gen py:new_style,utf8strings tests/pingpong.thrift
    ```

2. Write thrift app.

    ```python
    #! /usr/bin/env python
    # tests/app.py
    # -*- coding: utf-8 -*-

    from pingpong_sdk.pingpong import PingService

    class PingpongServer(object):
        def ping(self):
            if os.environ.get('about_to_shutdown') == '1':
                raise PingService.AboutToShutDownException
            return "pong"

    app = PingService.Processor(PingpongServer())
    ```

3. Fire up app.
    ```bash
    % gunicorn_thrift tests.app:app -k thrift_sync
    % gunicorn_thrift tests.app:app -k thrift_gevent
    ```

### Using `thriftpy`

1. Write thrift app.

    ```python
    #! /usr/bin/env python
    # tests/app.py
    # -*- coding: utf-8 -*-

    import thriftpy
    from thriftpy.thrift import TProcessor

    class PingPongDispatcher(object):
        def ping(self):
            return "pong"

    pingpong_thrift = thriftpy.load("pingpong.thrift")
    app = TProcessor(pingpong_thrift.PingService, PingPongDispatcher())
    ```

2. Fire up app.

    ```bash
    % gunicorn_thrift tests.thriftpy_app:app -k thriftpy_sync \
      --thrift-protocol-factory \
        thriftpy.protocol:TCyBinaryProtocolFactory \
      --thrift-transport-factory \
        thriftpy.transport:TCyBufferedTransportFactory
    ```

## Configs

### Workers

Parameter: `-k`, `--worker-class`
Config file: `worker_class`
Default 2.7: `thrift_sync`
Default 3.2+: `thriftpy_sync`

There are 4 types of workers available.

* `thrift_sync`: sync worker.
* `thrift_gevent`: gevent worker.
* `thriftpy_sync`: sync worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)
* `thriftpy_gevent`: gevent worker, adapted for [`thriftpy`](https://github.com/eleme/thriftpy)

note: If you want to use `thriftpy_sync` or `thriftpy_gevent`, make sure the following:

* Version of `thriftpy` should be higher than `0.1.10`.
* `--thrift-protocol-factory` should be set to either:  
    1. `thriftpy.protocol:TCyBinaryProtocolFactory` or
    1. `thriftpy.protocol:TBinaryProtocolFactory`
* `--thrift-transport-factory` should be set to either:  
    1. `thriftpy.transport:TCyBufferedTransportFactory` or
    1. `thriftpy.transport:TBufferedTransportFactory`


### Transport factory

The transport factory to use for handling connections.

Parameter: `--thrift-transport-factory`  
Config file: `thrift_transport_factory`  
Default 2.7: `thrift.transport.TTransport:TBufferedTransportFactory`  
Default 3.2+: `thriftpy.transport:TBufferedTransportFactory`


### Protocol factory

The protocol factory to use for parsing requests.

Parameter: `--thrift-protocol-factory`  
Config file: `thrift_protocol_factory`  
Default 2.7: `thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory`  
Default 3.2+: `thriftpy.protocol:TBinaryProtocolFactory`

### Client timeout

Seconds to timeout a client if it is silent after this duration.

Parameter: `--thrift-client-timeout`  
Config file: `thrift_client_timeout`  
Default: `None` (Never time out a client)
