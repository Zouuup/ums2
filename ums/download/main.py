# -*- coding: utf-8 -*-
""" initialize module command line parser.
"""

import ums
import ums.defaults
import json
from subprocess import call
from subprocess import check_output
import hashlib
import os
import re
import tarfile
import time
import shutil
import StringIO


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
        if os.path.isdir(local_file + '_'):
            shutil.rmtree(local_file + '_', True)
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

        @rtype :boolean
        @return False on fail (even in one option)

        """
        push = os.getcwd()
        os.chdir(local_file + '_')

        (dist, part) = dist.split('/')

        target = '/'.join([ums.defaults.QUILT_INJECTS,
                           dist,
                           package])
        if not os.path.isdir(target):
            return True  # Thats ok, no ptah

        for files in os.listdir(ums.defaults.QUILT_INJECTS):
            patch = '/'.join([ums.defaults.QUILT_INJECTS, files])
            if call(['quilt', 'import', patch]) != 0:
                return False

        return True

    @staticmethod
    def changelog_change(dist, package, local_file, maintainer):
        """made changelog changes.

        @type dist: string
        @param dist: dist (i.e : stable/main)

        @type package: string
        @param package: package to extract

        @type local_file: string
        @param local_file: file to extract

        @type maintainer: string
        @param maintainer: maintainer

        @rtype :boolean
        @return False on fail (even in one option)

        """
        (dist, part) = dist.split('/')
        print local_file + '_/changelog'
        os.rename(local_file + '_/debian/changelog',
                  local_file + '_/changelog__old')
        cl = file(local_file + '_/changelog__old', 'r')
        cl_out = file(local_file + '_/debian/changelog', 'w')
        # Need to alter first entry
        first = cl.readline()
        old_dist = re.search("[^)]*\)\s([^;]*)", first)
        try:
            old_dist = old_dist.group(1)
        except:
            return False
        cl_out.write(first.replace(old_dist + ';', dist + ';'))
        while True:
            line = cl.readline()
            if line[:4] == ' -- ':
                break
            cl_out.write(line)
        line = ' -- %s  %s\n' % (maintainer,
                                 time.strftime('%a, %d %b %Y %H:%M:%S %z'))
        cl_out.write(line)
        for l in cl:
            cl_out.write(l)
        cl.close()
        cl_out.close()

    @staticmethod
    def dsc_changse(dsc_file, maintainer, files):
        """Made dsc changes.

        @type dsc_file: string
        @param dsc_file: dsc file address

        @type maintainer: string
        @param maintainer: maintainer email (use this to sign)

        @type files: list
        @param files: list of files

        """
        # Detach sign
        data_string = check_output(['gpg', '-d', dsc_file])
        no_file = stringio.StringIO.StringIO(data_string)

        for line in no_file:
            if line[:1] != ' ':
                last_line = line
            if re.match("^Maintainer:.*", line):
                line = "Maintainer: " + maintainer
            elif re.match("^Uploaders:.*", line):
                line = "Uploaders: " + maintainer

        no_file = os.patch.splitext(dsc_file)[0]

        # Lets sign it after all changes

    @staticmethod
    def repack(tar):
        """Repack new file.

        @type tar: string
        @param tar: tar file address

        """
        file_name, file_extension = os.path.splitext(tar)
        os.unlink(tar)
        out = tarfile.open(tar, 'w:' + file_extension[1:])
        out.add(tar + '_/debian', arcname='debian')
        out.close()

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
        maintainer = json.loads(ums.redis.hget(job, '_Maintainer'))
        is_quilt = pkg_format.find('quilt') >= 0

        alist = json.loads(files)
        try_count = 0
        finished_list = []
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
                                              package,
                                              home + '/' + f_name,
                                              maintainer)
                    Download.repack(home + '/' + f_name)
                finished_list.append(f_name)

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
