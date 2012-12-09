# -*- coding: utf-8 -*-
"""Default values, DO NOT use as a config file.

No trailing slash for paths
"""

import os

MIRROR = 'http://ftp.us.debian.org/debian'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

REDIS_PREFIX = 'UMS:'
PACKAGES_INFIX = ':PACKAGES:'
PROVIDES_INFIX = ':PROVIDES:'
INSTALLED_INFIX = ':INSTALLED:'
ADDED_POSTFIX = ':ADDED'


DL_LIST = REDIS_PREFIX + 'DownloadList:'
BUILD_LIST = REDIS_PREFIX + 'BuildList:'

SLAVE_PREFIX = REDIS_PREFIX + 'Slave:'

HOME = '/tmp/ums'

STRICT = True

BLOCK_SIZE = 65536

TRY_COUNT = 3


QUILT_INJECTS = '/var/lib/ums/patches'
KEYS_PATH = '/var/lib/ums/keys'

os.environ['TZ'] = 'Asia/Tehran'
