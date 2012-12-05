# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""

import ums
import ums.defaults
import json


class DependencyWalker:

    """Dependency walker class."""

    package = ''
    base_channel = ''
    channel = ''
    prefered = ''
    source = {}
    max_level = 0
    level = 0
    ver = set()
    strict = True

    # Static variable, I hate Python!!!
    provides = set()

    redis = ums.redis

    def __init__(self, package, channel, max_level=0, ver=set(), strict=True):
        """Initialize object.

        @type package: string
        @param package: package name
        @type channel: string
        @param channel: channel string
        @type max_level: integer
        @param max_level: check max level
        @type ver: set
        @param ver: version conditions
        @type strict: boolean
        @param strict: strict mode?

        """
        self.base_channel = channel
        self.strict = strict
        self.max_level = max_level
        self.ver = ver
        self.package = package
        self.channel = []
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
        self.channel = []
        for i in all_pkgs[channel]:
            self.channel.append(i['source'])

    def check_provides(self):
        """check for provides package.

        @rtype: string
        @return provides list

        """

        #Check for provides
        for i in self.channel:
            provides = ums.defaults.REDIS_PREFIX + i.replace('/', '_').upper()
            provides += ums.defaults.PROVIDES_INFIX + self.package.upper()
            data = self.redis.exists(provides)
            if data:
                return provides
        #if self.strict:
        raise Exception('Can not find ' + self.package + ' in strict mode')

    def find_package(self):
        """find package.

        @rtype string
        @return result of search

        """

        for i in self.channel:
            key = ums.defaults.REDIS_PREFIX + i.replace('/', '_').upper()
            key += ums.defaults.PACKAGES_INFIX + self.package.upper()

            data = self.redis.exists(key)
            if data:
                return key

        return ''

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
        if self.prefered == '':  # Is this a Provides package?
            provides = self.check_provides()
            items = self.redis.smembers(provides)
            result = []
            for i in items:
                pkg_detail = i.split(':')
                dw = DependencyWalker(pkg_detail[1],
                                      pkg_detail[0],
                                      self.max_level,
                                      set(),
                                      self.strict)
                result.extend(dw.walk_dependency(level + 1))

            return result

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
        for i in result:
            dw = DependencyWalker(i,
                                  self.base_channel,
                                  self.max_level,
                                  result[i])
            real_result.extend(dw.walk_dependency(level))
        return real_result


class DependencyAdder:

    """A class to add dependency class to list."""

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

        version = ums.redis.hget(package, 'Version')

        old_version = ums.redis.get(key)
        if old_version:
            if version == old_version:
                return
        # First update new version
        ums.redis.set(key, version)
        # Push it to dl list
        ums.redis.lpush(ums.defaults.DL_LIST, key)


def init(args):
    """Initialize add module.

    @type args: Namespace
    @param args: module arguments

    """
    t = DependencyWalker(args.package,
                         args.source,
                         args.level,
                         set(),
                         args.strict)

    wd = t.walk_dependency()
    DependencyAdder.add_package(wd[0], args.asdep)
    del wd[0]
    for pkg_key in wd:
        DependencyAdder.add_package(pkg_key)
    ##

    print ums.redis.keys('*' + ums.defaults.ADDED_POSTFIX)
