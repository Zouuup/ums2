# -*- coding: utf-8 -*-
import ums.defaults
def init_subparser(sub_parser):
	""" init sub parser commands
	 @type sub_parser: ArgumentParser
	 @param sub_parser: sub parser to add sub commands
	"""

	config_parser = sub_parser.add_parser('config', help='config module')
	config_parser.add_argument('source', help='add new source something like unstable/main')
	config_parser.add_argument('arch', help='target architecture')
	config_parser.add_argument('target', help='target in xamin project like stable/main')
	config_parser.add_argument('--mirror', help='Mirror for use with this, default to ' + ums.defaults.MIRROR)
	config_parser.add_argument('--show', choices='yn' ,help='Show all registered source default n')

	config_parser.set_defaults(module = 'ums.config.main')
	config_parser.set_defaults(mirror = ums.defaults.MIRROR)
	config_parser.set_defaults(show = 'n')
	return
