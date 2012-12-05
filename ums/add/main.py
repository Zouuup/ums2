# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""

import ums
import ums.defaults
import json


class DependencyWalker:

    """Dependency walker class."""

    package = ''
    channel = ''
    prefered = ''
    source = {}
    max_level = 0
    level = 0
    ver = set()

    # Static variable, I hate Python!!!
    provides = set()

    redis = ums.redis

    def __init__(self, package, channel='', max_level=0, ver=set()):
        """Initialize object.

        @type package: string
        @param package: package name
        @type channel: string
        @param channel: channel string
        @type max_level: integer
        @param max_level: check max level
        @type ver: set
        @param ver: version conditions

        """
        self.max_level = max_level
        self.ver = ver
        self.package = package
        self.channel = ''
        if channel != '':
            self.find_channel(channel)

        self.prefered = self.find_package()

    def find_channel(self, channel):
        """find a channel.

        @type channel: string
        @param channel: channel string

        """

        all_pkgs = self.redis.get(ums.defaults.REDIS_PREFIX + 'sources')

        if not all_pkgs:
            all_pkgs = {}
        else:
            all_pkgs = json.loads(all_pkgs)

        if not channel in all_pkgs:
            raise Exception("The " + channel + " is not available")

        self.source = all_pkgs[channel]
        self.channel = channel

    def check_provides(self):
        """check for provides package."""

        #Check for provides
        provides = ums.defaults.REDIS_PREFIX + '*'
        provides += ums.defaults.PROVIDES_INFIX + self.package.upper()

        pkeys = self.redis.keys(provides)
        if len(pkeys) == 0:
            raise Exception('Package ' + self.package +
                            ' not found in any channel.')
        #There is a prefered channel
        if self.channel != '':
            prefered = ums.defaults.REDIS_PREFIX
            prefered += self.channel.replace('/', '_').upper()
            prefered += ums.defaults.PROVIDES_INFIX
            prefered += self.package.upper()

            if prefered in pkeys:
                DependencyWalker.provides.add(prefered)
                return

        if len(pkeys) == 1:
            DependencyWalker.provides.add(pkeys[0])
            return

        i = 1
        for key in pkeys:
            print i + ')' + key

        code = raw_input('What is your selection :')
        DependencyWalker.provides.add(pkeys[code])

    def find_package(self):
        """find package.

        @rtype string
        @return result of search

        """

        #TODO add check for version too
        key = ums.defaults.REDIS_PREFIX + '*'
        key += ums.defaults.PACKAGES_INFIX + self.package.upper()

        keys = self.redis.keys(key)

        #no prefered channel or that is not part of prefered channel
        #No package at all
        if len(keys) == 0:
            self.check_provides()
            # Then its a provid pkg
            #Do not set prefered. so its not checked with other dependency,
            return ''

        if self.channel != '':  # There is a prefered channel
            prefered = ums.defaults.REDIS_PREFIX
            prefered += self.channel.replace('/', '_').upper()
            prefered += ums.defaults.PACKAGES_INFIX
            prefered += self.package.upper()

            if prefered in keys:
                return prefered

        if len(keys) == 1:  # only one package
            return keys[0]

        i = 1
        for key in keys:
            print i + ')' + key

        code = raw_input('What is your selection :')
        return keys[code - 1]

    def parse_depends(self, depends):
        """parse depends part.

        @type depends: string
        @param depends: | seperated string

        @rtype list
        @return array of depends

        """

        # first check if | is available
        pkgs = depends.split('|')
        result = []
        for p in pkgs:
            parts = p.split('(')
            parts[0] = parts[0].strip(' )\n\t"')
            if len(parts) == 2:
                parts[1] = parts[1].strip(' )\n\t')
            result.append(parts)
        return result

    def walk_dependency(self, level=0):
        """real walker.

        @type level: integer
        @param level: current level

        @rtype list
        @return array of depends (in redis key strings)

        """
        if self.prefered == '':
            return []

        if level > self.max_level:
            return [self.prefered]
        level += 1

        tmp = []
        if self.redis.hexists(self.prefered, 'Depends'):
            depends = self.redis.hget(self.prefered, 'Depends').split(',')

            for dep in depends:
                tmp.extend(self.parse_depends(dep))

        if self.redis.hexists(self.prefered, 'Pre-Depends'):
            depends = self.redis.hget(self.prefered, 'Pre-Depends').split(',')

            for dep in depends:
                tmp.extend(self.parse_depends(dep))

        result = {}
        for pkg in tmp:
            if len(pkg) > 1:
                version = pkg[1]
            else:
                version = ''

            if pkg[0] in result:
                result[pkg[0]].add(version)
            else:
                result[pkg[0]] = set(version)

        #Now list is uniqe, walk for them
        real_result = [self.prefered]
        # First add Provides
        for p in DependencyWalker.provides:
            items = self.redis.smembers(p)
            for i in items:
                pkg_detail = i.split(':')
                dw = DependencyWalker(pkg_detail[1], pkg_detail[0], self.max_level)
                real_result.extend(dw.walk_dependency(level))

        DependencyWalker.provides = set()
        for i in result:
            dw = DependencyWalker(i, self.channel, self.max_level, result[i])
            real_result.extend(dw.walk_dependency(level))
        return real_result

class DependencyAdder:

    """A class to add dependency class to list"""

    @staticmethod
    def add_package(package, asdep=True):
        """Add package to lit of installed package.

        @type package: string
        @param package: package to add to the list

        @type asdep: boolean
        @param asdep: is this a dependency

        """
        # Add key is like this : $OLDKEY$:ADDED => version-installed
        key = package + ums.defaults.ADDED_POSTFIX
        version = ums.redis.hget(package, 'Version').strip('"')

        old_version = ums.redis.get(key)
        if old_version:
            if version == old_version:
                return
        # First update new version
        ums.redis.set(key, version)
        # Push it to dl list
        ums.redis.lpush(ums.defaults.DL_LIST)


def init(args):
    """Initialize add module.

    @type args: Namespace
    @param args: module arguments

    """

    t = DependencyWalker(args.package, args.source, args.level, set())

    wd = t.walk_dependency()
    DependencyAdder.add_package(wd[0], False)
    del wd[0]
    for pkg_key in wd:
        DependencyAdder.add_package(pkg_key)
    ##
