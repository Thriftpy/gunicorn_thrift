gunicorn_thrift
===============

[![Build Status](https://travis-ci.org/Thriftpy/gunicorn_thrift.svg?branch=master)](https://travis-ci.org/Thriftpy/gunicorn_thrift)
[![Coverage Status](https://coveralls.io/repos/github/Thriftpy/gunicorn_thrift/badge.svg?branch=master)](https://coveralls.io/github/Thriftpy/gunicorn_thrift?branch=master)

Thrift app and worker for gunicorn! Hence, a multi-process python thrift server!

## Why?

* graceful reload/shutdown.
* manage worker number at runtime.
* and everything else `gunicorn` has to offer.

## Supported Platforms

* Python 2.7, all worker classes
* Python 3.4+, `thriftpy_sync` and `thriftpy_gevent` worker classes (code generated
  using the Thrift toolkit is not supported on Python 3)

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

### Using `thriftpy2`

1. Write thrift app.

    ```python
    #! /usr/bin/env python
    # tests/app.py
    # -*- coding: utf-8 -*-

    import thriftpy2
    from thriftpy2.thrift import TProcessor

    class PingPongDispatcher(object):
        def ping(self):
            return "pong"

    pingpong_thrift = thriftpy2.load("pingpong.thrift")
    app = TProcessor(pingpong_thrift.PingService, PingPongDispatcher())
    ```

2. Fire up app.

    ```bash
    % gunicorn_thrift tests.thriftpy_app:app -k thriftpy_sync \
      --thrift-protocol-factory \
        thriftpy2.protocol:TCyBinaryProtocolFactory \
      --thrift-transport-factory \
        thriftpy2.transport:TCyBufferedTransportFactory
    ```

## Configs

### Workers

Parameter: `-k`, `--worker-class`
Config file: `worker_class`
Default 2.7: `thrift_sync`
Default 3.4+: `thriftpy_sync`

There are 4 types of workers available.

* `thrift_sync`: sync worker.
* `thrift_gevent`: gevent worker.
* `thriftpy_sync`: sync worker, adapted for [`thriftpy2`](https://github.com/thriftpy/thriftpy2)
* `thriftpy_gevent`: gevent worker, adapted for [`thriftpy2`](https://github.com/thriftpy/thriftpy2)

note: If you want to use `thriftpy_sync` or `thriftpy_gevent`, make sure the following:

* Version of `thriftpy2` should be higher than `0.1.10`.
* `--thrift-protocol-factory` should be set to either:  
    1. `thriftpy2.protocol:TCyBinaryProtocolFactory` or
    1. `thriftpy2.protocol:TBinaryProtocolFactory`
* `--thrift-transport-factory` should be set to either:  
    1. `thriftpy2.transport:TCyBufferedTransportFactory` or
    1. `thriftpy2.transport:TBufferedTransportFactory`


### Transport factory

The transport factory to use for handling connections.

Parameter: `--thrift-transport-factory`  
Config file: `thrift_transport_factory`  
Default 2.7: `thrift.transport.TTransport:TBufferedTransportFactory`  
Default 3.4+: `thriftpy2.transport:TBufferedTransportFactory`


### Protocol factory

The protocol factory to use for parsing requests.

Parameter: `--thrift-protocol-factory`  
Config file: `thrift_protocol_factory`  
Default 2.7: `thrift.protocol.TBinaryProtocol:TBinaryProtocolAcceleratedFactory`  
Default 3.4+: `thriftpy2.protocol:TBinaryProtocolFactory`

### Client timeout

Seconds to timeout a client if it is silent after this duration.

Parameter: `--thrift-client-timeout`  
Config file: `thrift_client_timeout`  
Default: `None` (Never time out a client)

### Gevent check interval

This config will run a seperate thread to detect gevent ioloop block every
specified seconds.

Parameter: `--gevent-check-interval`  
Config file: `gevent_check_interval`  
Default: 0  

Note: DONOT USE this if not running gevent worker.
