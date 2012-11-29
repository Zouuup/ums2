# -*- coding: utf-8 -*-
""" initialize module command line parser
"""

import ums.defaults


def init_subparser(sub_parser):
    """init sub parser commands.

    @type sub_parser: ArgumentParser
    @param sub_parser: sub parser to add sub commands

    """

    update_parser = sub_parser.add_parser('update', help='update module')

    update_parser.add_argument('target',
                               help='update which channels, default all',
                               nargs='?', default='all')

    update_parser.set_defaults(module='ums.update.main')
    return
