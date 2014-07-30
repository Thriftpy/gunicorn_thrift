# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.


import os
from setuptools import setup, Command
import sys

from gunicorn_thrift import __version__


CLASSIFIERS = [
    'Development Status :: Pre Alpha',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Network',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Network :: Thrift',
]

# read dev requirements
fname = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(fname) as f:
    REQUIREMENTS = list(map(lambda l: l.strip(), f.readlines()))


class PyTest(Command):
    user_options = [
        ("cov", None, "measure coverage")
    ]

    def initialize_options(self):
        self.cov = None

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        basecmd = [sys.executable, '-m', 'pytest']
        if self.cov:
            basecmd += ['--cov', 'gunicorn_thrift']
        errno = subprocess.call(basecmd + ['tests'])
        raise SystemExit(errno)

py_modules = []
tests_require = ['pytest', 'pytest-cov']

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

    tests_require=tests_require,
    cmdclass={'test': PyTest},

    install_requires=REQUIREMENTS,

    entry_points="""
    [console_scripts]
    gunicorn_thrift=gunicorn_thrift.app:run
    """
)
