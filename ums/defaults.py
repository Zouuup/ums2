# -*- coding: utf-8 -*-
"""Default values, do not use as a config file.
"""
MIRROR = 'http://ftp.us.debian.org/debian'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

REDIS_PREFIX = 'UMS:'
PACKAGES_INFIX = ':PACKAGES:'
PROVIDES_INFIX = ':PROVIDES:'
INSTALLED_INFIX = ':INSTALLED:'
ADDED_POSTFIX = ':ADDED'


DL_LIST = REDIS_PREFIX + 'DownloadList'
BUILD_LIST = REDIS_PREFIX + 'BuildList'

HOME = '/tmp/ums'
