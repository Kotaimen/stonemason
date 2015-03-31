# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/2/15'

import six
import unittest

from stonemason.pyramid import Pyramid, TileIndex, Tile, MetaTileIndex
from stonemason.provider.formatbundle import MapType
from stonemason.provider.tilestorage import NullClusterStorage
from stonemason.provider.tilestorage import ClusterStorage, TileCluster
from stonemason.provider.tileprovider import StorageTileProvider
from stonemason.provider.tileprovider import NullTileProvider


class TestNullTileProvider(unittest.TestCase):
    def setUp(self):
        self._provider = NullTileProvider()

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        cluster = self._provider.get_tilecluster(meta_index)
        self.assertIsNone(cluster)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        metatile = self._provider.get_metatile(meta_index)
        self.assertIsNone(metatile)


class DummyClusterStorage(ClusterStorage):
    def get(self, index):
        tiles = [
            Tile(index=TileIndex(1, 0, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 0, 1), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 1), data=six.b('A tile'))
        ]
        return TileCluster(index=index, tiles=tiles)


class TestStorageProviderWithDummyStorage(unittest.TestCase):
    def setUp(self):
        maptype = MapType()
        pyramid = Pyramid()

        storage = DummyClusterStorage()

        self._provider = StorageTileProvider(maptype, pyramid, storage)

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        cluster = self._provider.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            self.assertEqual(six.b('A tile'), tile.data)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        metatile = self._provider.get_metatile(meta_index)
        self.assertIsNone(metatile)


class TestStorageProviderWithNullStorage(unittest.TestCase):
    def setUp(self):
        maptype = MapType()
        pyramid = Pyramid()

        storage = NullClusterStorage()

        self._provider = StorageTileProvider(maptype, pyramid, storage)

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        cluster = self._provider.get_tilecluster(meta_index)
        self.assertIsNone(cluster)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        metatile = self._provider.get_metatile(meta_index)
        self.assertIsNone(metatile)


