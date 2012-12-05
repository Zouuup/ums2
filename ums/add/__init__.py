# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""


import ums.defaults


def init_subparser(sub_parser):
    """init sub parser commands.

    @type sub_parser: ArgumentParser
    @param sub_parser: sub parser to add sub commands

    """

    add_parser = sub_parser.add_parser('add', help='Add package to the flow')

    add_parser.add_argument('source',
                            help='package belongs to which repository')
    add_parser.add_argument('package',
                            help='target package to install')
    add_parser.add_argument('--asdep', type=bool,
                            help='Add as dependency ')
    add_parser.add_argument('--strict', type=bool,
                            help='Strict mode')

    add_parser.add_argument('--level', type=int,
                            help='Max walk level')

    add_parser.set_defaults(module='ums.add.main')
    add_parser.set_defaults(asdep=False)
    add_parser.set_defaults(strict=ums.defaults.STRICT)
    add_parser.set_defaults(level=3)
    return
