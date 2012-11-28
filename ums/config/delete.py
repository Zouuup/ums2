# -*- coding: utf-8 -*-
""" delete a repo from redis data
"""

import sys
import redis
import json
import ums.defaults


def init(args):
    """init current module with arguments from argparse library.

    delete one entry

    @type args: Namespace
    @param args: module arguments

    """
    all = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all:
        all = {}
    else:
        all = json.loads(all)

    if args.target in all:
        del all[args.target]
        ums.redis.set(ums.defaults.REDIS_PREFIX + 'sources', json.dumps(all))
        print "source removed"
    else:
        print "No added source for key " + args.target
