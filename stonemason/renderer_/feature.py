# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/19/15'

import io
from collections import namedtuple


_Feature = namedtuple('Feature', 'crs bounds size data')


class Feature(_Feature):  # pragma: no cover
    pass


class ImageFeature(Feature):
    def __new__(cls, crs=None, bounds=None, size=None, data=None):
        return Feature.__new__(
            cls, crs=crs, bounds=bounds, size=size, data=data)

    def __repr__(self):
        result = '%s(crs=%r, bounds=%r, size=%r)' % (
            self.__class__.__name__,
            self.crs,
            self.bounds,
            self.size,
        )
        return result

    def tobytes(self, fmt='PNG', parameters=None):
        buffer = io.BytesIO()

        if parameters is None:
            parameters = dict()

        self.data.save(buffer, format=fmt, parameters=parameters)

        raw_data = buffer.getvalue()

        return raw_data


class VectorFeature(Feature):
    pass


class RasterFeature(Feature):
    pass
