# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/9/15'

"""
    stonemason.provider.tilestorage.clusterfier
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Convert a `MetaTileStorage` to a `ClusterStorage` on-the-fly.
"""

from .tilestorage import ClusterStorage, MetaTileStorage
from .cluster import TileCluster


class Clusterfier(ClusterStorage):
    """Convert a `MetaTileStorage` to a `ClusterStorage` on-the-fly.

    :param storage: Given `MetaTileStorage` to clusterify.
    :type storage: :class:`~stonemason.provider.storage.MetaTileStorage`

    :param splitter: A :class:`~stonemason.provider.tilestorage.Splitter` instance
        to split `MetaTile` data into `Tile` data.
    :type splitter: :class:`~stonemason.provider.tilestorage.Splitter`
    """

    def __init__(self, storage, splitter=None):
        assert isinstance(storage, MetaTileStorage)
        self._storage = storage
        self._splitter = splitter

    def get(self, index):
        metatile = self._storage.get(index)
        if metatile is None:
            return None
        cluster = TileCluster.from_metatile(metatile, self._splitter)
        return cluster

    def put(self, metatile):
        self._storage.put(metatile)

    def retire(self, index):
        self._storage.retire(index)

    def close(self):
        self._storage.close()
