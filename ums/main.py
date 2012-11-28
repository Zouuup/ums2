# -*- coding: utf-8 -*-
"""
 Application entry point
"""

import ums.defaults
import argparse
import importlib
import redis
#just import the base to add sub commands
import ums.config


def main():
    """ Application entry point. """

    parser = argparse.ArgumentParser(prog='ums')

    parser.add_argument('--redis-host', help='Redis host default to ' +
                        ums.defaults.REDIS_HOST)
    parser.set_defaults(redis_host=ums.defaults.REDIS_HOST)

    parser.add_argument('--redis-port', type=int, help='Redis port default to '
                        + str(ums.defaults.REDIS_PORT))
    parser.set_defaults(redis_port=ums.defaults.REDIS_PORT)

    # Add sub parser for config module
    sub_parser = parser.add_subparsers(help='ums operations')
    ums.config.init_subparser(sub_parser)

    args = parser.parse_args()

    #initialize redis first
    ums.redis = redis.StrictRedis(host=args.redis_host,
                                  port=args.redis_port, db=0)

    ## Load selected module, then run init function
    mod = importlib.import_module(args.module)
    mod.init(args)
