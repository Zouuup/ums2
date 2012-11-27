# -*- coding: utf-8 -*-

import argparse
import importlib
#just import the base to add sub commands
import ums.config

def main():
	""" Application entry point """

	parser = argparse.ArgumentParser(prog='ums')

	# Add sub parser for config module
	sub_parser = parser.add_subparsers(help='ums operations')
	ums.config.init_subparser(sub_parser)


	args = parser.parse_args()
	## Load selected module, then run init function
	mod = importlib.import_module(args.module + '.main')

	mod.init(args);
