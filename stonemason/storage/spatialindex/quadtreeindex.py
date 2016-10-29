# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/28/16'

from stonemason.storage.concept import SpatialIndexConcept


class QuadTreeIndex(SpatialIndexConcept):
    def intersection(self, envelope):
        raise NotImplementedError
