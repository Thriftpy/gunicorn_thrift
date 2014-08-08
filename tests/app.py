#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pingpong_sdk.pingpong import PingService


class PingpongServer(object):
    def ping(self):
        if os.environ.get('about_to_shutdown') == '1':
            raise PingService.AboutToShutDownException
        return "pong"

app = PingService.Processor(PingpongServer())
