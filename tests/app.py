#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pingpong_sdk.pingpong import PingService


class PingpongServer(object):
    def ping(self):
        print("Receive ping")
        return "pong"

app = PingService.Processor(PingpongServer())
