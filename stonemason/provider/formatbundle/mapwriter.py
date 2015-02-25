# -*- encoding: utf-8 -*-
"""
    stonemason.provider.formatbundle.mapwriter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Map serializers.
"""

__author__ = 'kotaimen'
__date__ = '2/19/15'

import io

from PIL import Image

from stonemason.util.postprocessing.gridcrop import shave, grid_crop_into_data

from .exceptions import NoMatchingMapWriter
from .tileformat import TileFormat
from .maptype import MapType


class MapWriter(object):  # pragma: no cover
    """Serialize rendered map as tile data.

    :param tile_format: Tile format of the bundle.
    :type tile_format: :class:`~stonemason.provider.formatbundle.TileFormat`
    """

    def __init__(self, tile_format):
        assert isinstance(tile_format, TileFormat)
        self._format = tile_format

    @property
    def real_map_type(self):
        """Real map object type. (python `type`)"""
        raise NotImplementedError

    def crop_map(self, map, buffer=0):
        """ Crop a map object and serialize it into tile data.

        :param map: Map data.
        :param buffer: Size of the buffer, default is ``0``.
        :type buffer: int
        :return: Cropped map and serialized data.
        :rtype: bytes
        """
        raise NotImplementedError

    def grid_crop_map(self, map, stride=1, buffer=0):
        """ Crop a map object into grids and serialize into tile data.

        :param map: Map data.

        :param stride: Number of grid images per axis.
        :type stride: int

        :param buffer: Size of the buffer to be shaved each side in pixels,
                            default is 0, means no buffer is shaved.
        :type buffer: int

        :return: A iterator of ``((row, column), data)``
        :rtype: iterator
        """
        raise NotImplementedError

    def resplit_map(self, data, stride=1, buffer=0):
        """ Re-corp a metatile data object into tiles.

        Same as :meth:`grid_crop_map` except this method accepts
        :class:`~stonemason.provider.pyramid.MetaTile` data instead of map data.

        :param data: Metatile data.

        :param stride: Number of grid images per axis.
        :type stride: int

        :param buffer: Size of the buffer to be shaved each side in pixels,
                            default is 0, means no buffer is shaved.
        :type buffer: int

        :return: A iterator of ``((row, column), data)``
        :rtype: iterator
        """
        raise NotImplementedError


class ImageMapWriter(MapWriter):
    """Write map image as tile data, use PIL/Pillow as ImageIO."""

    @property
    def real_map_type(self):
        return Image.Image

    def crop_map(self, map_, buffer=0):
        assert isinstance(map_, Image.Image)
        image = shave(map_, buffer_size=buffer)
        buf = io.BytesIO()
        image.save(buf,
                   format=self._format.format,
                   **self._format.parameters)
        return buf.getvalue()

    def grid_crop_map(self, map_, stride=1, buffer=0):
        assert isinstance(map_, Image.Image)
        return grid_crop_into_data(map_,
                                   stride=stride,
                                   buffer_size=buffer,
                                   format=self._format.format,
                                   parameters=self._format.parameters)

    def resplit_map(self, data, stride=1, buffer=0):
        assert isinstance(data, bytes)
        return grid_crop_into_data(data,
                                   stride=stride,
                                   buffer_size=buffer,
                                   format=self._format.format,
                                   parameters=self._format.parameters)


def find_writer(map_type, tile_format):
    # TODO: Figure out how to register map writers dynamically until we have more writers
    assert isinstance(map_type, MapType)
    assert isinstance(tile_format, TileFormat)

    if map_type.type == 'image' and tile_format.mimetype.startswith('image/'):
        return ImageMapWriter(tile_format)
    else:
        raise NoMatchingMapWriter(tile_format.format)
