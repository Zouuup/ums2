# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""

import ums
import ums.defaults
import json
from subprocess import call
import hashlib
import os
import re
import tarfile


class Download:

    """Download package and prepare for xamin."""

    @staticmethod
    def download_a_file(mirror, repo, package, f_name, target):
        """Download a file.

        @type mirror: string
        @param mirror: mirror address

        @type repo: string
        @param repo: channel (like stable/main)

        @type package: string
        @param package: package name

        @type f_name: string
        @param f_name: file name to download

        @type target: string
        @param target: target folder to put downloaded file

        @rtype : integer
        @return wget return code

        """

        (dummy, needed) = repo.split('/')
        source = '/'.join([mirror, 'pool',
                           needed, package[:1],
                           package, f_name])
        return call(['wget', '-c', '-O', target + '/' + f_name, source])

    @staticmethod
    def check_md5_sum(md5, f_name, target):
        """chack md5 hash of file.

        @type md5: string
        @param md5: expected md5

        @type f_name: string
        @param f_name: file name to check

        @type target: string
        @param target: file folder

        @rtype: boolean
        @return false if fails

        """
        afile = open(target + '/' + f_name)
        hasher = hashlib.md5()
        buf = afile.read(ums.defaults.BLOCK_SIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(ums.defaults.BLOCK_SIZE)

        return md5 == hasher.hexdigest()

    @staticmethod
    def listen_to_change():
        """Pop a value from a list (download list).

        @rtype: tuple
        @return the result (key, value)

        """

        raise Exception("Not yet :)")
        return ums.redis.brpop(ums.defaults.DL_LIST)

    @staticmethod
    def return_job_to_list(uid, job):
        """Return job to list, if can not do that job.

        @type uid: string
        @param uid: yniq id for current slave

        @type job: string
        @param job: key to download

        """
        ums.redis.lpush(ums.defaults.DL_LIST, job)
        ums.redis.delete(ums.defaults.SLAVE_PREFIX + uid.upper())

    @staticmethod
    def extract_quilt(job, local_file):
        """Extract quilt files.

        @type job: string
        @param job: key to download

        @type local_file: string
        @param local_file: file to extract

        """
        tar = tarfile.open(local_file)
        os.mkdir(local_file + '_')
        tar.extractall(local_file + '_')

    @staticmethod
    def inject_patchs(dist, package, local_file):
        """Inject patchs.

        @type dist: string
        @param dist: dist (i.e : stable/main)

        @type package: string
        @param package: package to extract

        @type local_file: string
        @param local_file: file to extract

        """
        #TODO
        None

    @staticmethod
    def changelog_change(dist, package, local_file):
        """made changelog changes.

        @type dist: string
        @param dist: dist (i.e : stable/main)

        @type package: string
        @param package: package to extract

        @type local_file: string
        @param local_file: file to extract

        """

        #TODO
        None

    @staticmethod
    def dsc_changse():
        """Made dsc changes. """
        #TODO
        None

    @staticmethod
    def repack():
        """Repack new file."""
        #TODO
        None

    @staticmethod
    def fix_dsc_file():
        """fix and sign main dsc file."""
        #TODO
        None

    @staticmethod
    def check_for_old_jobs(uid, home):
        """Check for slave key and continue old job.

        @type uid: string
        @param uid: slave uniq id

        @type home: string
        @param home: home folder to save result

        """

        job = ums.redis.get(ums.defaults.SLAVE_PREFIX + uid.upper())
        if not job:
            return

        # Job is key to real package
        files = ums.redis.hget(job, 'Files')
        package = json.loads(ums.redis.hget(job, 'Package'))
        source = json.loads(ums.redis.hget(job, '_Source'))
        target = json.loads(ums.redis.hget(job, '_Target'))
        mirror = json.loads(ums.redis.hget(job, '_Mirror'))
        pkg_format = json.loads(ums.redis.hget(job, 'Format'))
        is_quilt = pkg_format.find('quilt') >= 0

        alist = json.loads(files)
        try_count = 0
        try:
            while True:
                f = alist.pop()
                if try_count > ums.defaults.TRY_COUNT:
                    Download.return_job_to_list(uid, job)
                    return
                # Files is 3 part , size, md5 and file name
                (md5, size, f_name) = f.split(' ')
                Download.download_a_file(mirror, source, package, f_name, home)
                if not Download.check_md5_sum(md5, f_name, home):
                    try_count += 1
                    os.unlink(home + '/' + f_name)
                    alist.append(f)  # Push it back, try again
                if is_quilt and f_name.find('debian.tar') >= 0:
                    Download.extract_quilt(job,
                                           home + '/' + f_name)
                    Download.inject_patchs(target,
                                           package,
                                           home + '/' + f_name)
                    Download.changelog_change(target,
                                              source,
                                              package,
                                              home + '/' + f_name)
                    Download.dsc_changse()
                    Download.repack()

        except IndexError:
            pass


def init(args):
    """Initialize download module.

    @type args: Namespace
    @param args: module arguments

    """

    home = args.home
    uid = args.uid
    # Simply, loop and watch
    while ums.redis.ping():
        # Check if a job is waiting
        Download.check_for_old_jobs(uid, home)
        result = Download.listen_to_change()
        if result:  # None on timeout
            # Time to add this a s a key
            (ky, job) = result
            ums.redis.set(ums.defaults.SLAVE_PREFIX + uid.upper(), job)
