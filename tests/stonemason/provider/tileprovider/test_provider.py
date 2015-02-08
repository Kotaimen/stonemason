# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/2/15'

import six
import unittest

from stonemason.provider.pyramid import Pyramid, TileIndex, Tile
from stonemason.provider.tilecache import TileCache
from stonemason.provider.tilestorage import ClusterStorage, TileCluster
from stonemason.provider.tileprovider import TileProviderBuilder, TileProvider


class DummyTileCache(TileCache):
    def __init__(self):
        self._cache = dict()

    def get(self, tag, index):
        self._cache.get((tag, index))

    def put(self, tag, tile, ttl=0):
        self._cache[(tag, tile.index)] = tile


class DummyClusterStorage(ClusterStorage):
    def get(self, index):
        tiles = [
            Tile(index=TileIndex(1, 0, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 0, 1), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 1), data=six.b('A tile'))
        ]
        return TileCluster(index=index, tiles=tiles)


class TestNullProvider(unittest.TestCase):
    def setUp(self):
        p = Pyramid()
        self._provider = TileProvider(tag='null', pyramid=p)

    def test_tag(self):
        self.assertEqual('null', self._provider.tag)

    def test_metadata(self):
        self.assertDictEqual(dict(), self._provider.metadata)

    def test_get_tile(self):
        self.assertIsNone(self._provider.get_tile(0, 0, 0))


class TestDummyProvider(unittest.TestCase):
    def setUp(self):
        t = 'test'
        p = Pyramid()
        m = dict(scale=2)
        s = DummyClusterStorage()

        self._provider = TileProvider(t, pyramid=p, metadata=m, storage=s)

    def test_tag(self):
        self.assertEqual('test', self._provider.tag)

    def test_metadata(self):
        self.assertDictEqual(dict(scale=2), self._provider.metadata)

    def test_get_tile(self):
        z, x, y = 1, 0, 0
        tile = self._provider.get_tile(z, x, y)

        self.assertEqual(TileIndex(z, x, y), tile.index)
        self.assertEqual(six.b('A tile'), tile.data)


class TestTileProviderFactory(unittest.TestCase):
    def test_create_tile_provider(self):
        t = 'test'
        m = dict(attribution='K&R')
        p = Pyramid()
        cache_config = dict(prototype='null')
        storage_config = dict(prototype='null')

        builder = TileProviderBuilder(tag=t, pyramid=p)
        builder.build_metadata(attribution='K&R')
        builder.build_cache(**cache_config)
        builder.build_storage(**storage_config)

        provider = builder.build()

        self.assertEqual(t, provider.tag)
        self.assertDictEqual(m, provider.metadata)
        self.assertDictEqual(p._asdict(), provider.pyramid._asdict())
