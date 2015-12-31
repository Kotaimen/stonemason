# -*- coding:utf-8 -*-

"""
    stonemason.util.tempfn
    ~~~~~~~~~~~~~~~~~~~~~~
    Generate a temp filename
"""

__author__ = 'ray'
__date__ = '8/30/12'

import os
import errno
import tempfile

import six


STONEMASON_TEMP_ROOT = 'stonemason'


def generate_temp_filename(dirname=None, prefix='tmp', suffix=''):
    """Generate a temporary file name with specified suffix and prefix.

    >>> from stonemason.util.tempfn import generate_temp_filename
    >>> generate_temp_filename('/tmp', prefix='hello-', suffix='.tmp') #doctest: +ELLIPSIS
    '/tmp/hello-....tmp'

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
        dirname = os.path.join(tempfile.gettempdir(), STONEMASON_TEMP_ROOT)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    for n, temp in enumerate(tempfile._get_candidate_names()):
        basename = '%s%s%s' % (prefix, temp, suffix)
        return os.path.join(dirname, basename)

    raise IOError(errno.EEXIST, 'Exhausted temporary file names.')
