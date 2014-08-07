gunicorn_thrift
===============

[![Build Status](https://travis-ci.org/wooparadog/gunicorn_thrift.svg?branch=master)](https://travis-ci.org/wooparadog/gunicorn_thrift)

Thrift app and workder for gunicorn!

## Why?

* graceful reload/shutdown.
* manage worker number at runtime.
* and everything else `gunicorn` has to offer.

## Examples

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
