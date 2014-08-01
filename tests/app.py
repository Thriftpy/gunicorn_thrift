#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pingpong_sdk.pingpong import PingService


class PingpongServer(object):
    def ping(self):
        return "pong"

app = PingService.Processor(PingpongServer())
