# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import six

from ..concept import StorageKeyConcept, ObjectSerializeConcept


class FeatureKeyConcept(StorageKeyConcept):  # pragma: no cover
    pass


class SimpleFeatureKeyMode(FeatureKeyConcept):
    def __call__(self, index):
        assert isinstance(index, six.string_types)
        return index



