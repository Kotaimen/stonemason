# -*- encoding: utf-8 -*-
"""
    stonemason.provider.formatbundle.mapwriter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Map serializers.
"""

__author__ = 'kotaimen'
__date__ = '2/19/15'

import io
from abc import ABCMeta, abstractmethod

import six
from PIL import Image

from stonemason.util.postprocessing.gridcrop import shave, grid_crop_into_data

from .exceptions import NoMatchingMapWriter
from .tileformat import TileFormat
from .maptype import MapType


class MapWriter(object):
    def __init__(self, tile_format):
        assert isinstance(tile_format, TileFormat)
        self._format = tile_format

    def crop_map(self, map, buffer=0):
        raise NotImplementedError

    def grid_crop_map(self, map, stride=1, buffer=0):
        raise NotImplementedError

    def resplit_map(self, data, stride=1, buffer=0):
        raise NotImplementedError


class ImageMapWriter(MapWriter):
    def crop_map(self, map_, buffer=0):
        assert isinstance(map_, Image.Image)
        image = shave(map_, buffer_size=buffer)
        buf = io.BytesIO()
        image.save(buf, format=self._format.format,
                   **self._format.parameters)
        return buf.getvalue()

    def grid_crop_map(self, map_, stride=1, buffer=0):
        assert isinstance(map_, Image.Image)
        return grid_crop_into_data(map_, stride=stride, buffer_size=buffer)

    def resplit_map(self, data, stride=1, buffer=0):
        assert isinstance(data, bytes)
        return grid_crop_into_data(data, stride=stride, buffer_size=buffer)


def find_writer(tile_format, map_type=None):
    # TODO: Figure out how to register map writers dynamically until we have more writers
    assert isinstance(tile_format, TileFormat)
    if tile_format.mimetype.startswith('image/'):
        if map_type is not None:
            map_type.type == 'image'
        return ImageMapWriter(tile_format)
    else:
        raise NoMatchingMapWriter(tile_format.format)
