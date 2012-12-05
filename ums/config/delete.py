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
    all_pkgs = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all_pkgs:
        all_pkgs = {}
    else:
        all_pkgs = json.loads(all_pkgs)

    if args.target in all_pkgs:
        if args.partial == '':
            del all_pkgs[args.target]
        else:
            for i in all_pkgs[args.target]:
                if i['source'] == args.partial:
                    del all_pkgs[args.target][all_pkgs[args.target].index(i)]

        ums.redis.set(ums.defaults.REDIS_PREFIX + 'sources',
                      json.dumps(all_pkgs))
        print "source removed"
    else:
        print "No added source for key " + args.target
