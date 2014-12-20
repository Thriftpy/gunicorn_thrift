# -*- coding: utf-8 -*-

import sys
import pytest

requires_py27 = pytest.mark.skipif(sys.version_info[:2] != (2, 7),
                                   reason='requires py27')

