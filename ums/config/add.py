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
        'target': args.target,
        'maintainer': args.email}

    all_pkgs = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all_pkgs:
        all_pkgs = {}
    else:
        all_pkgs = json.loads(all_pkgs)

    if args.target in all_pkgs:
        new_value = all_pkgs[args.target]
    else:
        new_value = []

    for i in new_value:
        if i['source'] == args.source:
            print "Source is already part of target"
            return

    if args.priority < 0:
        args.priority = 0
    if args.priority > len(new_value):
        args.priority = len(new_value)

    new_value.insert(args.priority, repo)
    all_pkgs[args.target] = new_value
    ums.redis.set(ums.defaults.REDIS_PREFIX + 'sources', json.dumps(all_pkgs))

    print "Source added successfuly"
