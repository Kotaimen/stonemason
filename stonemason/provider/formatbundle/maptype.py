# -*- encoding: utf-8 -*-

"""
    stonemason.provider.formatbundle.maptype
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Map types.
"""

__author__ = 'kotaimen'
__date__ = '2/19/15'

import collections

from .exceptions import InvalidMapType

_MapType = collections.namedtuple('_MapType', 'type')


class MapType(_MapType):
    """The result `type` produced by a map renderer.

    The following map types are supported:

    ``image``
        Ordinary image for final map presentation.
        Usually the actual object type is :class:`PIL.Image.Image`.

    ``raster``
        Geo-referenced raster (eg: ``GeoTIFF``, ``DEM``).

    ``feature``
        Geography feature (aka: `vector`).

    >>> from stonemason.provider.formatbundle import MapType
    >>> maptype = MapType('image')
    >>> maptype
    MapType(image)

    :param type: Type of the map.
    :type type: str
    """
    __slots__ = ()

    KNOWN_TYPES = {'raster', 'image', 'feature'}

    def __new__(cls, type='image'):
        if type not in cls.KNOWN_TYPES:
            raise InvalidMapType(type)

        return _MapType.__new__(cls, type)

    def __repr__(self):
        return 'MapType(%s)' % self.type
