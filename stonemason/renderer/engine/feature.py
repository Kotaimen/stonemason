# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/19/15'

from collections import namedtuple

_Feature = namedtuple('Feature', 'crs bounds size data')


class Feature(_Feature):  # pragma: no cover
    def __new__(cls, crs=None, bounds=None, size=None, data=None):
        return _Feature.__new__(
            cls, crs=crs, bounds=bounds, size=size, data=data)

    def __repr__(self):
        result = '%s(crs=%r, bounds=%r, size=%r)' % (
            self.__class__.__name__,
            self.crs,
            self.bounds,
            self.size,
        )
        return result

