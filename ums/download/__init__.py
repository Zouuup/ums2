# -*- coding: utf-8 -*-
""" initialize module command line parser
"""

import ums.defaults


def init_subparser(sub_parser):
    """init sub parser commands.

    @type sub_parser: ArgumentParser
    @param sub_parser: sub parser to add sub commands

    """

    download_parser = sub_parser.add_parser('download', help='download module')
    download_parser.add_argument('uid',
                                 help='Uniq id for this slave')
    h = 'target folder to store result into, '
    h += 'the home folder is used to store file.'
    dhownload_parser.add_argument('tfolder',
                                  help=h)

    download_parser.set_defaults(module='ums.download.main')

    return
