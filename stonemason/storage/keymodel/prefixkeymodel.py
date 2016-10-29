# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/29/16'

import os
import six

from stonemason.storage.concept import StorageKeyConcept


class PrefixKeyMode(StorageKeyConcept):
    def __init__(self, prefix='', sep='/'):
        assert isinstance(prefix, six.string_types)
        self._prefix = prefix
        self._sep = sep

    def __call__(self, index):
        assert isinstance(index, six.string_types)
        return os.path.normpath(self._sep.join([self._prefix, index]))
