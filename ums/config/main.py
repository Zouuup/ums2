# -*- coding: utf-8 -*-
import sys

def init(args):
	""" init current module with arguments from argparse library
	"""

	if args.source and args.url:
		print "source or url, not both at the same time"
		sys.exit(1)
