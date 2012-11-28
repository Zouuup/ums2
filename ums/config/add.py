# -*- coding: utf-8 -*-
""" Save and load configs inside redis,
    Configs are json data
"""

import sys
import redis
import json
import ums.defaults


def init(args):
    """init current module with arguments from argparse library.

    save current upstream repository to redis

    @type args: Namespace
    @param args: module arguments

    """
    repo = {
        'mirror': args.mirror,
        'arch': args.arch,
        'source': args.source,
        'target': args.target}

    all = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all:
        all = {}
    else:
        all = json.loads(all)

    all[args.target] = repo
    ums.redis.set(ums.defaults.REDIS_PREFIX + 'sources', json.dumps(all))

    print "Source added successfuly"
