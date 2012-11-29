# -*- coding: utf-8 -*-
""" initialize module command line parser
"""

import ums.defaults


def init_subparser(sub_parser):
    """init sub parser commands.

    @type sub_parser: ArgumentParser
    @param sub_parser: sub parser to add sub commands

    """

    config_parser = sub_parser.add_parser('config', help='config module')

    config_sub_parser = config_parser.add_subparsers(help='config operations')
    ## Add
    add_parser = config_sub_parser.add_parser('add', help='add a repo')

    add_parser.add_argument('source',
                            help='add new source something like unstable/main')
    add_parser.add_argument('arch',
                            help='target architecture')
    add_parser.add_argument('target',
                            help='target in xamin project like stable/main')
    add_parser.add_argument('--mirror',
                            help='Mirror for use with this, default to '
                            + ums.defaults.MIRROR)

    add_parser.set_defaults(module='ums.config.add')
    add_parser.set_defaults(mirror=ums.defaults.MIRROR)

    ## Delete
    del_parser = config_sub_parser.add_parser('del', help='delete a repo')
    del_parser.add_argument('target', help='xamin repository name to delete')
    del_parser.set_defaults(module='ums.config.delete')

    ## Show
    show_parser = config_sub_parser.add_parser(
        'show',
        help='show list of registeed repo')
    show_parser.set_defaults(module='ums.config.show')

    return
