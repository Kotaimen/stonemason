# -*- encoding: utf-8 -*-

"""
    stonemason.formatbundle.maptype
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Map types.
"""

__author__ = 'kotaimen'
__date__ = '2/19/15'

import collections

from .exceptions import InvalidMapType

_MapType = collections.namedtuple('_MapType', 'type')


class MapType(_MapType):
    """The map `type` produced by a cartographer.

    The following map types are known:

    ``image``
        Map generated from image processing or simple grid analysis
        Data type for `image` is :class:`PIL.Image.Image`.

    ``raster``
        Geo-referenced multi band spatial raster, usually from satellite
        imaging or data elevation model.
        Data type for `raster` is :class:`osgeo.gdal.Dataset`.

    ``feature``
        OSR simple geometry features.
        Data type for `feature` is :class:`osgeo.ogr.Feature`.

    ``graphics``
        Vector graphics.

    ``tin``
        Triangulated irregular network for surface/terrain visualization and
        analysis.

    ``cloud``
        Point cloud data from 3D laser scanning.

    >>> from stonemason.formatbundle import MapType
    >>> maptype = MapType('image')
    >>> maptype
    MapType(image)

    :param type: Type of the map.
    :type type: str
    """
    __slots__ = ()

    KNOWN_TYPES = {
        'raster', 'image',
        'feature', 'graphics',
        'tin', 'cloud'
    }

    def __new__(cls, type='image'):
        if type not in cls.KNOWN_TYPES:
            raise InvalidMapType(type)

        return _MapType.__new__(cls, type)

    def __repr__(self):
        return 'MapType(%s)' % self.type


