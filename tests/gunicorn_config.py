# -*- coding: utf-8 -*-

import os


def worker_term(worker):
    os.environ['about_to_shutdown'] = "1"


def on_connected(worker, addr):
    worker.log.info("connected: %s", addr)
