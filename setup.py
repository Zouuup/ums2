# -*- coding: utf-8 -*-
""" Setup" for pip
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
long_description = f.read()
f.close()


setup(
    name='Ums2',
    version='0.2.0',
    author='fzerorubigd',
    author_email='fzerorubigd@gmail.com',
    packages=['ums'],
    scripts=['bin/ums'],
    url='http://xamin.ir',
    license='LICENSE.md',
    description='Upstream management system for Xamin.',
    long_description=long_description,
    install_requires=[
        "redis>=2.7.0"
    ],
)
