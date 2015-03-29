# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/27/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import MapType


class TileProvider(object):  # pragma: no cover
    def __init__(self, maptype, pyramid):
        assert isinstance(maptype, MapType)
        assert isinstance(pyramid, Pyramid)
        self._maptype = maptype
        self._pyramid = pyramid

    @property
    def maptype(self):
        return self._maptype

    @property
    def pyramid(self):
        return self._pyramid

    def get_tilecluster(self, meta_index):
        raise NotImplementedError

    def get_metatile(self, meta_index):
        raise NotImplementedError


class NullTileProvider(TileProvider):
    def __init__(self, **kwargs):
        TileProvider.__init__(self, MapType(), Pyramid())

    def get_tilecluster(self, meta_index):
        return None

    def get_metatile(self, meta_index):
        return None
