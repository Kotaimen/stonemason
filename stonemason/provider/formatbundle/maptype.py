# -*- encoding: utf-8 -*-

"""
    stonemason.provider.formatbundle.maptype
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Map types
"""

__author__ = 'kotaimen'
__date__ = '2/19/15'

import collections

from .exceptions import InvalidMapType

_MapType = collections.namedtuple('_MapType', 'type')


class MapType(_MapType):
    """Type of map

    """
    __slots__ = ()

    KNOWN_TYPES = ['raster', 'image', 'feature']

    def __new__(cls, type='image'):
        if type not in cls.KNOWN_TYPES:
            raise InvalidMapType(type)

        return _MapType.__new__(cls, type)
