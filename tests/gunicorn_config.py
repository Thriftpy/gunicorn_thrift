# -*- coding: utf-8 -*-

import os


def worker_term(worker):
    os.environ['about_to_shutdown'] = "1"
