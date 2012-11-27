# -*- coding: utf-8 -*-

def init_subparser(sub_parser):
	""" init sub parser commands
	 @type sub_parser: ArgumentParser
	 @param sub_parser: sub parser to add sub commands
	"""

	config_parser = sub_parser.add_parser('config', help='config module')
	config_parser.add_argument('--source', help='add new source something like wheezy/main')
	config_parser.add_argument('--url', help='url to add instead of source like ftp://ftp.debian.org/debian/dists/wheezy/main')

	config_parser.set_defaults(module = 'ums.config')
	return
