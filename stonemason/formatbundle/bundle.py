# -*- encoding: utf-8 -*-


"""
    stonemason.formatbundle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Bundles map/tile format definition and conversion.
"""

__author__ = 'kotaimen'
__date__ = '2/17/15'

from .maptype import MapType
from .tileformat import TileFormat
from .mapwriter import find_writer, MapWriter


class FormatBundle(object):
    """ Bundles map type and tile format together and try finding a
    matching writer.

    >>> from stonemason.formatbundle import MapType, TileFormat, FormatBundle
    >>> format = FormatBundle(MapType('image'), TileFormat('JPEG'))
    >>> format
    FormatBundle(MapType(image), TileFormat(JPEG|image/jpeg|.jpg))
    >>> format.map_type
    MapType(image)
    >>> format.tile_format
    TileFormat(JPEG|image/jpeg|.jpg)
    >>> format.writer.real_map_type
    <class 'PIL.Image.Image'>

    :param map_type: Map type of the bundle.
    :type map_type: :class:`~stonemason.formatbundle.MapType`

    :param tile_format: Tile format of the bundle.
    :type tile_format: :class:`~stonemason.formatbundle.TileFormat`

    :raises: :exc:`~stonemason.formatbundle.NoMatchingMapWriter`
    """

    def __init__(self, map_type, tile_format):
        assert isinstance(map_type, MapType)
        assert isinstance(tile_format, TileFormat)
        self._map_type = map_type
        self._tile_format = tile_format

        self._writer = find_writer(map_type, tile_format)
        assert isinstance(self._writer, MapWriter)

    @property
    def writer(self):
        """Map writer of the bundle."""
        return self._writer

    @property
    def map_type(self):
        """Map type of the bundle."""
        return self._map_type

    @property
    def tile_format(self):
        """Tile format of the bundle."""
        return self._tile_format

    def __repr__(self):
        return 'FormatBundle(%r, %r)' % (self._map_type, self._tile_format)
