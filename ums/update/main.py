# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""

import ums
import json
from ums.update.download import download
import ums.update.parser


def init(args):
    """Initialize update module.

    @type args: Namespace
    @param args: module arguments

    """

    all_source = ums.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

    if not all_source:
        all_source = {}
    else:
        all_source = json.loads(all_source)

    update_list = []
    if args.target == 'all':
        for key in all_source:
            update_list.append(all_source[key])
    else:
        for key in all_source:
            if key == args.target:
                update_list.append(all_source[key])

    for entry in update_list:
        ret_code = download(args.home, entry)
        if ret_code != 0:
            print "Can not download " + entry['source']
            + ' from ' + entry['mirror']
            return
        ums.update.parser.parse_sources(args.home, entry)
