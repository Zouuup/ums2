# -*- coding: utf-8 -*-
"""Download an entry from source.
"""

from subprocess import call
import os


def download(home, entry_all):
    """Download an entry from source.

    @type home: string
    @param home: home directory
    @type entry_all: dictonary
    @param entry_all: data entry from redis

    @rtype int
    @return the wget return code

    """
    for entry in entry_all:
        i = entry_all.index(entry)
        address = entry['mirror'] + '/dists/' + entry['source']
        address = address + '/source/Sources.bz2'
        target = home + '/' + entry['target'].replace('/', '_')
        target += str(i) + '.Sources.bz2'

        if not os.path.exists(home):
            try:
                os.makedirs(home)
            except:
                print "Can not create directory"
                raise

        ret_code = call(['wget', '-c', '-O', target, address])
        if ret_code == 0:
            address = entry['mirror'] + '/dists/' + entry['source']
            address = address + '/' + entry['arch'] + '/Packages.bz2'
            target = home + '/' + entry['target'].replace('/', '_')
            target += str(i) + '.Packages.bz2'
            ret_code = call(['wget', '-c', '-O', target, address])
        if ret_code != 0:
            return ret_code

    return ret_code
