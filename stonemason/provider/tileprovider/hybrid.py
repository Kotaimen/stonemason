# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

from stonemason.tilestorage import TileCluster, ClusterStorage
from stonemason.renderer.tilerenderer import MetaTileRenderer

from .provider import TileProvider


class HybridTileProvider(TileProvider):
    def __init__(self, bundle, pyramid, storage, renderer):
        TileProvider.__init__(self, bundle, pyramid)
        assert isinstance(renderer, MetaTileRenderer)
        assert isinstance(storage, ClusterStorage)
        self._storage = storage
        self._renderer = renderer

    def get_tilecluster(self, meta_index):
        cluster = self._storage.get(meta_index)
        if cluster is not None:
            return cluster

        metatile = self.get_metatile(meta_index)
        if metatile is None:
            return None

        cluster = TileCluster.from_metatile(metatile, self._bundle.writer)

        return cluster

    def get_metatile(self, meta_index):
        metatile = self._renderer.render_metatile(meta_index)
        return metatile
