# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/24/15'

import unittest

from stonemason.provider.tilecache import NullTileCache
from stonemason.provider.pyramid import Tile, TileIndex


class TestNullTileCache(unittest.TestCase):
    def test_nullcache(self):
        cache = NullTileCache()
        self.assertIsNone(cache.put('tag', Tile(TileIndex(3, 4, 5))))
        self.assertIsNone(cache.get('tag', TileIndex(3, 4, 5)))
        self.assertFalse(cache.has('tag', TileIndex(3, 4, 5)))
        self.assertFalse(cache.has_all('tag', []))



if __name__ == '__main__':
    unittest.main()
