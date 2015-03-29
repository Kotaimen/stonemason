# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

from stonemason.provider.formatbundle import FormatBundle
from stonemason.provider.tilestorage import TileCluster
from stonemason.renderer.tilerenderer import MetaTileRenderer

from .provider import TileProvider


class RendererTileProvider(TileProvider):
    def __init__(self, maptype, pyramid, bundle, renderer):
        TileProvider.__init__(self, maptype, pyramid)
        assert isinstance(bundle, FormatBundle)
        assert isinstance(renderer, MetaTileRenderer)
        self._bundle = bundle
        self._renderer = renderer

    def get_tilecluster(self, meta_index):
        metatile = self.get_metatile(meta_index)
        if metatile is None:
            return None

        cluster = TileCluster.from_metatile(metatile, self._bundle.writer)
        return cluster

    def get_metatile(self, meta_index):
        metatile = self._renderer.render_metatile(meta_index)
        return metatile
