# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/19/15'

import re
from collections import namedtuple

_Feature = namedtuple('Feature', 'crs bounds size data')


class Feature(_Feature):  # pragma: no cover
    pass


class ImageFeature(Feature):
    def __new__(cls, crs=None, bounds=None, size=None, data=None):
        return Feature.__new__(
            cls, crs=crs, bounds=bounds, size=size, data=data)

    def __repr__(self):
        result = re.sub('^Feature', self.__class__.__name__,
                        Feature.__repr__(self))
        return result


class VectorFeature(Feature):
    pass


class RasterFeature(Feature):
    pass
