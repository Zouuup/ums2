# -*- coding: utf-8 -*-
""" delete a repo from redis data
"""

import sys
import redis
import json
import ums.defaults


def init(args):
    """init current module with arguments from argparse library.

    show all entries

    @type args: Namespace
    @param args: module arguments

    """
    all = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all:
        all = {}
    else:
        all = json.loads(all)

    print json.dumps(all, sort_keys=True, indent=4)
