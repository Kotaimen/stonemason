# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

from stonemason.provider.tilestorage import ClusterStorage

from .provider import TileProvider


class StorageTileProvider(TileProvider):
    def __init__(self, bundle, pyramid, storage):
        TileProvider.__init__(self, bundle, pyramid)
        assert isinstance(storage, ClusterStorage)
        self._storage = storage

    def get_tilecluster(self, meta_index):
        cluster = self._storage.get(meta_index)
        return cluster

    def get_metatile(self, meta_index):
        return None
