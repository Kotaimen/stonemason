# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/15/15'

import unittest
import time

from stonemason.pyramid import Tile, TileIndex
from stonemason.tilecache import MemTileCache, TileCacheError
from tests import skipUnlessHasLocalMemcacheServer


@skipUnlessHasLocalMemcacheServer()
class TestMemTileCache(unittest.TestCase):
    def setUp(self):
        self.cache = MemTileCache(binary=False)

        self.cache.flush()

        self.cache.connection.set('layer/2/2/3',
                                  b'tile')
        self.cache.connection.set('layer/2/2/3~metadata',
                                  '["text/plain", 1234.56, "abcd"]')

        self.cache.connection.set('layer/3/4/5',
                                  b'a tile')

        self.cache.connection.set('layer/3/4/5~metadata',
                                  '["text/plain", 1234.56, "ABCD"]')

        self.cache.connection.set('badlayer/0/0/0',
                                  b'bad metadata')
        self.cache.connection.set('badlayer/0/0/0~metadata',
                                  'bad metadata')


    def tearDown(self):
        self.cache.close()

    def test_put(self):
        index = TileIndex(3, 4, 5)
        timestamp = time.time()
        tile = Tile(index, b'another tile', 'text/plain', timestamp)
        self.cache.put('another-layer', tile)
        self.assertTrue(self.cache.has('another-layer', TileIndex(3, 4, 5)))

    def test_get(self):
        tile = self.cache.get('layer', TileIndex(3, 4, 5))
        self.assertEqual(tile.index, (3, 4, 5))
        self.assertEqual(tile.mimetype, 'text/plain')
        self.assertEqual(tile.mtime, 1234.56)
        self.assertEqual(tile.etag, 'ABCD')

        self.assertIsNone(self.cache.get('layer', TileIndex(0, 0, 0)))

        self.assertRaises(TileCacheError,
                          self.cache.get,
                          'badlayer', TileIndex(0, 0, 0))

    def test_has(self):
        self.assertTrue(self.cache.has('layer', TileIndex(3, 4, 5)))
        self.assertFalse(self.cache.has('layer', TileIndex(3, 4, 6)))
        self.assertFalse(self.cache.has('layer1', TileIndex(3, 4, 5)))

    def test_retire(self):
        self.assertTrue(self.cache.has('layer', TileIndex(2, 2, 3)))
        self.cache.retire('layer', TileIndex(2, 2, 3))
        self.assertFalse(self.cache.has('layer', TileIndex(2, 2, 3)))

    def test_put_multi(self):
        tiles = [Tile(TileIndex(2, 2, 3), b'tile1', 'text/plain', 1.2),
                 Tile(TileIndex(3, 4, 5), b'tile2', 'text/plain', 1.2),
                 Tile(TileIndex(5, 6, 7), b'tile3', 'text/plain', 1.2), ]
        self.cache.put_multi('layer2', tiles)

        self.cache.has_all('layer2', [TileIndex(2, 2, 3),
                                      TileIndex(3, 4, 5),
                                      TileIndex(5, 6, 7)])

    def test_put_ttl(self):
        index = TileIndex(2, 2, 3)
        timestamp = time.time()
        tile = Tile(index, b'another tile', 'text/plain', timestamp)
        self.cache.put('ttl-test-layer', tile, 1)
        self.assertTrue(self.cache.has('ttl-test-layer', TileIndex(2, 2, 3)))
        time.sleep(1.1)
        self.assertFalse(self.cache.has('ttl-test-layer', TileIndex(2, 2, 3)))

    def test_lock(self):
        index = TileIndex(2, 2, 3)
        cas = self.cache.lock('lock-test-layer', index, 0.1)
        self.assertNotEqual(cas, 0)
        self.assertEqual(self.cache.lock('lock-test-layer', index, 1), 0)
        self.assertFalse(self.cache.unlock('lock-test-layer', index, 1234))
        self.assertTrue(self.cache.unlock('lock-test-layer', index, cas))
        self.assertTrue(self.cache.unlock('lock-test-layer', index, cas))


    def test_stats(self):
        self.assertTrue(self.cache.stats())


@skipUnlessHasLocalMemcacheServer()
class TestMemTileCacheConnectionFailure(unittest.TestCase):
    def test_conn_fail(self):
        self.assertRaises(TileCacheError,
                          MemTileCache,
                          servers=['0.0.0.0:80'])


if __name__ == '__main__':
    unittest.main()
