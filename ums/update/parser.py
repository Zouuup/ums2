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
    order = []

    def re_initialize(self):
        """Re initialize class."""
        self.result = {}
        self.order = []
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
            self.order.append(data[0].strip())
            if data[1].strip(' \t\n') == '':
                self.result[data[0]] = []
                self.last_array_data = True
            else:
                self.result[data[0]] = data[1].replace('"', ' ').strip(' \n\t')
                self.last_array_data = False

    def repack(self):
        """Repack into source structure.

        @rtype: string
        @return recreated file

        """
        res = ''
        for i in self.order:
            if isinstance(self.result[i], list):
                res += i + ':\n'
                for j in self.result[i]:
                    res += ' ' + j.encode() + '\n'
            else:
                res += i + ': ' + self.result[i] + '\n'
        return res

    def set_if_exists(self, index, data):
        """Set this if already exists.

        @type index: string
        @param index: index to replace

        @type data: anything
        @param data: data for insert

        """
        if index in self.result:
            self.result[index] = data

    def save_toredis(self, pipe, channel):
        """Save to redis.

        @type pipe: redis
        @param pipe: redis (or pipeline)
        @type channel: string
        @param channel: channel string

        """

        channel = channel.replace('/', '_').upper()
        key = ums.defaults.REDIS_PREFIX + channel + ums.defaults.PACKAGES_INFIX

        #pipe = redis.pipeline()
        if 'Binary' in self.result:
            pkgs = self.result['Binary'].split(',')
        else:
            pkgs = [self.result['Package']]

        for pkg in pkgs:
            new_key = key + pkg.strip(' \t\n').upper()
            for hkey in self.result:
                pipe.hset(new_key, hkey, json.dumps(self.result[hkey]))
        #pipe.execute()

    def save_some_toredis(self, pipe, channel, target_channel):
        """Save to redis.

        @type pipe: redis
        @param pipe: redis (or pipeline)
        @type channel: string
        @param channel: channel string
        @type target_channel: string
        @param target_channel: channel string

        """

        channel = channel.replace('/', '_').upper()
        key = ums.defaults.REDIS_PREFIX + channel + ums.defaults.PACKAGES_INFIX
        key = key + self.result['Package'].strip(' \t\n').upper()

        keys = ['Depends', 'Pre-Depends', 'Provides']
        for hkey in keys:
            if hkey in self.result:
                pipe.hset(key, hkey, json.dumps(self.result[hkey]))

        if 'Provides' in self.result:
            key = ums.defaults.REDIS_PREFIX + channel
            key += ums.defaults.PROVIDES_INFIX
            provides = self.result['Provides'].strip(' \t\n').split(',')
            for p in provides:
                new_key = key + p.strip(' \t\n').upper()
                try:
                    pipe.sadd(new_key,
                              target_channel + ':' +
                              self.result['Package'].strip(' \t\n'))
                except ValueError:
                    # it's no big deal as it's related to parsing
                    # QUEUED string as int which is default response
                    # callback of SADD command.
                    pass


def parse_sources(home, entry_all):
    """Save to redis.

    @type home: string
    @param home: home directory
    @type entry_all: list
    @param entry_all: entry from redis

    """
    for entry in entry_all:
        i = entry_all.index(entry)
        source = home + '/' + entry['target'].replace('/', '_')
        source += str(i) + '.Sources.bz2'

        f = bz2.BZ2File(source)

        ums.redis.execute_command('MULTI')

        data = SourcesParser()
        data.re_initialize()

        while True:
            line = f.readline()

            # Its the end of stream, not an empty splitter
            if line == '':
                break

            if line.strip(' \t\n') == "":
                data.add_line('_Mirror: ' + entry['mirror'])
                data.add_line('_Source: ' + entry['source'])
                data.add_line('_Target: ' + entry['target'])
                data.add_line('_Maintainer: ' + entry['maintainer'])
                data.save_toredis(ums.redis, entry['source'])
                data.re_initialize()
            else:
                data.add_line(line.strip('\n'))

        # just parse depends and pre-depends on this file
        package = home + '/' + entry['target'].replace('/', '_')
        package += str(i) + '.Packages.bz2'

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
            data.save_some_toredis(ums.redis, entry['source'], entry['target'])
            data.re_initialize()
        else:
            data.add_line(line.strip('\n'))

    ums.redis.execute_command('EXEC')

    print "Repository Updated successfully!"
