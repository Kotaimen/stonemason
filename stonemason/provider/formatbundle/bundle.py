# -*- encoding: utf-8 -*-


"""
    stonemason.provider.formatbundle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Bundles map/tile format definition and conversion.
"""

__author__ = 'kotaimen'
__date__ = '2/17/15'

from .maptype import MapType
from .tileformat import TileFormat
from .mapwriter import find_writer, MapWriterConcept


class FormatBundle(object):
    def __init__(self, map_type, tile_format):
        assert isinstance(map_type, MapType)
        assert isinstance(tile_format, TileFormat)
        self._map_type = map_type
        self._tile_format = tile_format

        self._writer = find_writer(map_type, tile_format)
        assert isinstance(self._writer, MapWriterConcept)

    @property
    def writer(self):
        return self.writer