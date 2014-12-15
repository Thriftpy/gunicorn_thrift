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
