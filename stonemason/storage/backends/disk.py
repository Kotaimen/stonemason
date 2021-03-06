# -*- encoding: utf-8 -*-
"""
    stonemason.storage.backends.disk
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements disk backend for storage module.
"""
__author__ = 'ray'
__date__ = '10/22/15'

import os
import sys
import six
import errno

from stonemason.util.tempfn import generate_temp_filename

from stonemason.storage.concept import PersistentStorageConcept


def safe_makedirs(name):
    try:
        # exist_ok option only available on python3
        os.makedirs(name)
    except OSError as e:  # pragma: no cover
        if e.errno == errno.EEXIST:
            # Ignore "already exists" error because os.makedirs
            # does not check dir exists at each creation step
            pass
        else:
            raise


class DiskStorage(PersistentStorageConcept):
    """Disk Storage

    The ``DiskStorage`` uses regular filesystem as persistence backend.

    """

    def exists(self, key):
        return os.path.exists(key)

    def retrieve(self, key):
        pathname = key
        if not os.path.exists(pathname):
            # not exist
            return None, None

        with open(pathname, 'rb') as fp:
            blob = fp.read()
        mtime = os.stat(pathname).st_mtime

        metadata = {'LastModified': mtime}

        return blob, metadata

    def store(self, key, blob, metadata):
        assert isinstance(key, six.string_types)
        assert isinstance(blob, bytes)
        assert isinstance(metadata, dict)

        pathname = key

        dirname, basename = os.path.split(pathname)

        # create directory first
        if not (os.path.exists(pathname) and os.path.isdir(pathname)):
            safe_makedirs(dirname)

        # generate temp file name
        tempname = generate_temp_filename(dirname, prefix=basename)

        with open(tempname, 'wb') as fp:
            fp.write(blob)

        # move it into place
        if sys.platform == 'win32':
            if os.path.exists(pathname):
                # os.rename is not atomic on windows
                os.remove(pathname)

        os.rename(tempname, pathname)

    def retire(self, key):
        pathname = key
        try:
            os.unlink(pathname)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # file not found, ignore
                pass
            else:
                raise

    def close(self):
        pass
