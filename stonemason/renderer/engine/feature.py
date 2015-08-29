# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.feature
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The interface of render result.
"""
__author__ = 'ray'
__date__ = '4/19/15'

from collections import namedtuple

_Feature = namedtuple('Feature', 'crs bounds size data')


class Feature(_Feature):  # pragma: no cover
    """Render Feature

    A `Feature` is a area of geographic object returned by a render node. It is
    a blob of data that is proper geo referenced.

    :param crs: The coordinate reference system of the feature.
    :type crs: str
    :param bounds: a tuple of ``(left, bottom, right, top)`` that represents
        boundary of the feature.
    :type bounds: tuple
    :param size: a tuple of ``(width, height)`` that represents the pixel size
        of the area of the feature.
    :type size: tuple
    :param data: feature data.
    :type data: any

    """
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

