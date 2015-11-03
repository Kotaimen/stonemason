# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

from ..concept import StorageError


class FeatureStorageError(StorageError):
    pass


class InvalidFeatureIndex(FeatureStorageError):
    pass
