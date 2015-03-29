# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

from .provider import TileProvider
from .renderer import RendererTileProvider
from .storage import StorageTileProvider


class HybridTileProvider(TileProvider):
    def __init__(self, storage_provider, renderer_provider):
        assert isinstance(storage_provider, StorageTileProvider)
        assert isinstance(renderer_provider, RendererTileProvider)
        assert storage_provider.maptype == renderer_provider.maptype
        assert storage_provider.pyramid == renderer_provider.pyramid
        TileProvider.__init__(
            self, storage_provider.maptype, storage_provider.pyramid)
        self._storage_provider = storage_provider
        self._renderer_provider = renderer_provider

    def get_tilecluster(self, meta_index):
        cluster = self._storage_provider.get_tilecluster(meta_index)
        if cluster is not None:
            return cluster

        cluster = self._renderer_provider.get_tilecluster(meta_index)

        return cluster

    def get_metatile(self, meta_index):
        metatile = self._renderer_provider.get_metatile(meta_index)
        return metatile
