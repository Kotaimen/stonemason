# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/2/15'

import six
import unittest

from stonemason.provider.pyramid import TileIndex, Tile
from stonemason.provider.tilecache import TileCache
from stonemason.provider.tilestorage import ClusterStorage
from stonemason.provider.tileprovider import TileProvider, TileProviderFactory


class DummyTileCache(TileCache):
    def __init__(self):
        self._cache = dict()

    def get(self, tag, index):
        self._cache.get((tag, index))

    def put(self, tag, tile, ttl=0):
        self._cache[(tag, tile.index)] = tile


class DummyClusterStorage(ClusterStorage):
    def get(self, index):
        return Tile(index=index, data='A tile')


class TestProvider(unittest.TestCase):
    def setUp(self):
        tag = 'test'
        metadata = dict(scale=2)
        storage = DummyClusterStorage()

        self._provider = TileProvider(tag, metadata=metadata, storage=storage)

    def test_tag(self):
        self.assertEqual('test', self._provider.tag)

    def test_metadata(self):
        self.assertDictEqual(dict(scale=2), self._provider.metadata)

    def test_get_tile(self):
        z, x, y = 0, 0, 0
        tile = self._provider.get_tile(z, x, y)

        self.assertEqual(TileIndex(z, x, y), tile.index)
        self.assertEqual(six.b('A tile'), tile.data)


class TestTileProviderFactory(unittest.TestCase):
    def test_create_tile_provider(self):
        tag = 'test'
        cache_conf = dict(prototype='null')
        storage_conf = dict(prototype='null')

        provider = TileProviderFactory().create(
            tag=tag,
            cache_conf=cache_conf,
            storage_conf=storage_conf
        )

        assert isinstance(provider, TileProvider)
