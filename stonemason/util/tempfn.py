# -*- coding:utf-8 -*-

__author__ = 'ray'
__date__ = '8/30/12'

import os
import errno
import tempfile

import six


def generate_temp_filename(dirname=None, prefix='tmp', suffix=''):
    """Generate a temporary file name with specified suffix and prefix.


    :param dirname: Base temp directory, default is system temp dir.
    :type dirname: str
    :param prefix: Prefix of the temporary file name, default is ``tmp``
    :type prefix: str
    :param suffix: Suffix of the temporary file name, default is emptry string.
    :type suffix: str
    :return: Generated temporary file name.
    :rtype: str
    :raises: :class:`IOError`
    """
    assert isinstance(suffix, six.string_types)
    assert isinstance(prefix, six.string_types)

    if not dirname:
        dirname = tempfile.gettempdir()

    for n, temp in enumerate(tempfile._get_candidate_names()):
        basename = '%s%s%s' % (prefix, temp, suffix)
        return os.path.join(dirname, basename)

    raise IOError(errno.EEXIST, 'Exhausted temporary file names.')
