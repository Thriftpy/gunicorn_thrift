#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

import thriftpy
from thriftpy.thrift import TProcessor

from . import AboutToShutDownException

pingpong_thrift = thriftpy.load(
    os.path.join(
        os.path.dirname(__file__),
        "pingpong.thrift"
        )
    )
PingService = pingpong_thrift.PingService


class PingpongServer(object):
    def ping(self):
        if os.environ.get('about_to_shutdown') == '1':
            raise AboutToShutDownException
        return "pong"


app = TProcessor(pingpong_thrift.PingService, PingpongServer())
