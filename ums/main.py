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
import ums.update
import ums.add
import ums.download
from os import mkdir,path

def main():
    """ Application entry point. """

    parser = argparse.ArgumentParser(prog='ums')

    parser.add_argument('--redis-host', help='Redis host default to ' +
                        ums.defaults.REDIS_HOST)
    parser.set_defaults(redis_host=ums.defaults.REDIS_HOST)

    parser.add_argument('--redis-port', type=int, help='Redis port default to '
                        + str(ums.defaults.REDIS_PORT))
    parser.set_defaults(redis_port=ums.defaults.REDIS_PORT)

    parser.add_argument('--home',
                        help='folder to store data inside, '
                        + 'must have full access to it, defaults to: '
                        + ums.defaults.HOME)
    parser.set_defaults(home=ums.defaults.HOME)

    # Add sub parser for config module
    sub_parser = parser.add_subparsers(help='ums operations')
    ums.config.init_subparser(sub_parser)
    ums.update.init_subparser(sub_parser)
    ums.add.init_subparser(sub_parser)
    ums.download.init_subparser(sub_parser)

    args = parser.parse_args()

    # Making sure HOME directory is created
    if path.isdir(args.home) != True:
        mkdir (args.home)

    # initialize redis first
    ums.redis = redis.StrictRedis(host=args.redis_host,
                                  port=args.redis_port, db=0)

    ## Load selected module, then run init function
    mod = importlib.import_module(args.module)
    mod.init(args)
