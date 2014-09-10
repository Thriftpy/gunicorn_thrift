# -*- coding: utf-8 -

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

from gunicorn_thrift import __version__


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

# read dev requirements
fname = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(fname) as f:
    REQUIREMENTS = list(map(lambda l: l.strip(), f.readlines()))

# read dev requirements
fname = os.path.join(os.path.dirname(__file__), 'test_requirements.txt')
with open(fname) as f:
    TEST_REQUIREMENTS = list(map(lambda l: l.strip(), f.readlines()))


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'tests', '--cov', 'gunicorn_thrift', '--cov-report',
            'term-missing', '--cov-config', '.coveragerc',
            ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

py_modules = []

for root, folders, files in os.walk('gunicorn_thrift'):
    for f in files:
        if f.endswith('.py'):
            full = os.path.join(root, f[:-3])
            parts = full.split(os.path.sep)
            modname = '.'.join(parts)
            py_modules.append(modname)


setup(
    name='gunicorn_thrift',
    version=__version__,

    description='Thrift server using gunicorn',
    author='Haochuan Guo',
    author_email='guohaochuan@gmail.com',
    license='MIT',

    classifiers=CLASSIFIERS,
    zip_safe=False,
    py_modules=py_modules,
    include_package_data=True,

    tests_require=TEST_REQUIREMENTS,
    cmdclass={'test': PyTest},

    install_requires=REQUIREMENTS,

    entry_points="""
    [console_scripts]
    gunicorn_thrift=gunicorn_thrift.thriftapp:run
    """
)
