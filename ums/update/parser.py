# -*- coding: utf-8 -*-
"""Parse Packages data and put them inside redis
"""

import json
import bz2
import ums.defaults


class SourcesParser:

    """Data parser. """

    result = {}

    last_index = False
    last_data = False
    last_array_data = False

    def re_initialize(self):
        """Re initialize class."""
        self.result = {}
        self.last_index = False
        self.last_array_data = False

    def add_line(self, line):
        """add new line.

        @type line: string
        @param line: the new line to add

        """
        if line[:1] == ' ':
            if not self.last_array_data:
                self.result[self.last_index] += line.rstrip()
            else:
                self.result[self.last_index].append(line.strip())
        else:
            data = line.strip('\n').split(':', 1)
            if len(data) != 2:
                raise Exception('invalid line: ' + line)

            self.last_index = data[0].strip()
            if data[1].strip(' \t\n') == '':
                self.result[data[0]] = []
                self.last_array_data = True
            else:
                self.result[data[0]] = data[1].strip()
                self.last_array_data = False

    def save_toredis(self, redis, channel):
        """Save to redis.

        @type redis: redis
        @param redis: redis (or pipeline)
        @type channel: string
        @param channel: channel string

        """

        channel = channel.replace('/', '_').upper()
        key = ums.defaults.REDIS_PREFIX + channel + ums.defaults.PACKAGES_INFIX

        pipe = redis.pipeline()
        if 'Binary' in self.result:
            pkgs = self.result['Binary'].split(',')
        else:
            pkgs = [self.result['Package']]

        for pkg in pkgs:
            new_key = key + pkg.strip(' \t\n').upper()
            for hkey in self.result:
                pipe.hset(new_key, hkey, json.dumps(self.result[hkey]))
        pipe.execute()

    def save_some_toredis(self, redis, channel):
        """Save to redis.

        @type redis: redis
        @param redis: redis (or pipeline)
        @type channel: string
        @param channel: channel string

        """

        channel = channel.replace('/', '_').upper()
        key = ums.defaults.REDIS_PREFIX + channel + ums.defaults.PACKAGES_INFIX
        key = key + self.result['Package'].strip(' \t\n').upper()

        pipe = redis.pipeline()
        keys = ['Depends', 'Pre-Depends']
        for hkey in keys:
            if hkey in self.result:
                pipe.hset(key, hkey, json.dumps(self.result[hkey]))
        pipe.execute()


def parse_sources(home, entry):
    """Save to redis.

    @type home: string
    @param home: home directory
    @type entry: list
    @param entry: entry from redis

    """

    source = home + '/' + entry['target'].replace('/', '_') + '.Sources.bz2'

    f = bz2.BZ2File(source)

    data = SourcesParser()
    data.re_initialize()

    while True:
        line = f.readline()

        # Its the end of stream, not an empty splitter
        if line == '':
            break

        if line.strip(' \t\n') == "":
            data.save_toredis(ums.redis, entry['source'])
            data.re_initialize()
        else:
            data.add_line(line.strip('\n'))

    # just parse depends and pre-depends on this file
    package = home + '/' + entry['target'].replace('/', '_') + '.Packages.bz2'

    f = bz2.BZ2File(package)

    data = SourcesParser()
    data.re_initialize()

    current = False
    while True:
        line = f.readline()

        # Its the end of stream, not an empty splitter
        if line == '':
            break

        if line.strip(' \t\n') == "":
            data.save_some_toredis(ums.redis, entry['source'])
            data.re_initialize()
        else:
            data.add_line(line.strip('\n'))

    print "Updatet successfully"
