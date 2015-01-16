# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/15/15'

import unittest
import time

from stonemason.provider.pyramid import Tile, TileIndex
from stonemason.provider.tilecache import MemTileCache


class TestMemTileCache(unittest.TestCase):
    def setUp(self):
        self.cache = MemTileCache(binary=False)
        self.cache.connection.set('layer/2/3/4',
                                  b'tile')
        self.cache.connection.set('layer/2/3/4~metadata',
                                  '["text/plain", 1234.56, "abcd"]')

        self.cache.connection.set('layer/3/4/5',
                                  b'a tile')
        self.cache.connection.set('layer/3/4/5~metadata',
                                  '["text/plain", 1234.56, "ABCD"]')

    def tearDown(self):
        self.cache.close()

    def test_put(self):
        index = TileIndex(2, 3, 4)
        timestamp = time.time()
        tile = Tile(index, b'another tile', 'text/plain', timestamp)
        self.cache.put('another-layer', tile)
        self.assertTrue(self.cache.has('another-layer', TileIndex(2, 3, 4)))

    def test_get(self):
        tile = self.cache.get('layer', TileIndex(3, 4, 5))
        self.assertEqual(tile.index, (3, 4, 5))
        self.assertEqual(tile.mimetype, 'text/plain')
        self.assertEqual(tile.mtime, 1234.56)
        self.assertEqual(tile.etag, 'ABCD')

    def test_has(self):
        self.assertTrue(self.cache.has('layer', TileIndex(3, 4, 5)))
        self.assertFalse(self.cache.has('layer', TileIndex(3, 4, 6)))
        self.assertFalse(self.cache.has('layer1', TileIndex(3, 4, 5)))

    def test_retire(self):
        self.assertTrue(self.cache.has('layer', TileIndex(2, 3, 4)))
        self.cache.retire('layer', TileIndex(2, 3, 4))
        self.assertFalse(self.cache.has('layer', TileIndex(2, 3, 4)))

    def test_put_multi(self):
        tiles = [Tile(TileIndex(2, 3, 4), b'tile1', 'text/plain', 1.2),
                 Tile(TileIndex(3, 4, 5), b'tile2', 'text/plain', 1.2),
                 Tile(TileIndex(5, 6, 7), b'tile3', 'text/plain', 1.2), ]
        self.cache.put_multi('layer2', tiles)

        self.cache.has_all('layer2', [TileIndex(2, 3, 4),
                                      TileIndex(3, 4, 5),
                                      TileIndex(5, 6, 7)])

    def test_put_ttl(self):
        index = TileIndex(2, 3, 4)
        timestamp = time.time()
        tile = Tile(index, b'another tile', 'text/plain', timestamp)
        self.cache.put('ttl-test-layer', tile, 1)
        self.assertTrue(self.cache.has('ttl-test-layer', TileIndex(2, 3, 4)))
        time.sleep(1)
        self.assertFalse(self.cache.has('ttl-test-layer', TileIndex(2, 3, 4)))


    def test_stats(self):
        self.assertTrue(self.cache.stats())


if __name__ == '__main__':
    unittest.main()