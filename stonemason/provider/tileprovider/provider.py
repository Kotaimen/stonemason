# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/27/15'

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import MapType, TileFormat, FormatBundle


class TileProvider(object):  # pragma: no cover
    def __init__(self, bundle, pyramid):
        assert isinstance(bundle, FormatBundle)
        assert isinstance(pyramid, Pyramid)
        self._bundle = bundle
        self._pyramid = pyramid

    @property
    def formatbundle(self):
        return self._bundle

    @property
    def pyramid(self):
        return self._pyramid

    def get_tilecluster(self, meta_index):
        raise NotImplementedError

    def get_metatile(self, meta_index):
        raise NotImplementedError


class NullTileProvider(TileProvider):
    def __init__(self):
        dummy_bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        dummy_pyramid = Pyramid()
        TileProvider.__init__(self, dummy_bundle, dummy_pyramid)

    def get_tilecluster(self, meta_index):
        return None

    def get_metatile(self, meta_index):
        return None
