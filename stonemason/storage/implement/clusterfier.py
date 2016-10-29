# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/9/15'

from stonemason.formatbundle import MapWriter
from stonemason.pyramid.cluster import TileCluster
from .metatilestorage import MetaTileStorageConcept

ClusterStorage = MetaTileStorageConcept


class Clusterfier(ClusterStorage):
    """Convert a `MetaTileStorage` to a `ClusterStorage` on-the-fly.

    :param storage: Given `MetaTileStorage` to clusterify.
    :type storage: :class:`~stonemason.provider.storage.MetaTileStorage`

    :param writer: A `MapWriter` to resplit metatile data into small tiles.
    :type writer: :class:`~stonemason.formatbundle.MapWriter`
    """

    def __init__(self, storage, writer):
        assert isinstance(storage, MetaTileStorageConcept)
        assert isinstance(writer, MapWriter)

        self._storage = storage
        self._writer = writer

    @property
    def levels(self):
        return self._storage.levels

    @property
    def stride(self):
        return self._storage.stride

    def get(self, index):
        metatile = self._storage.get(index)
        if metatile is None:
            return None
        cluster = TileCluster.from_metatile(metatile, self._writer)
        return cluster

    def put(self, metatile):
        self._storage.put(metatile)

    def has(self, index):
        return self._storage.has(index)

    def retire(self, index):
        self._storage.retire(index)

    def close(self):
        self._storage.close()
