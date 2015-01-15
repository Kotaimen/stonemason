# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/15/15'

import unittest
import time

from stonemason.provider.pyramid import Tile, TileIndex
from stonemason.provider.tilecache import MemTileCache


class TestMemTileCache(unittest.TestCase):
    def setUp(self):
        self.cache = MemTileCache()

    def tearDown(self):
        self.cache.close()

    def test_put(self):
        index = TileIndex(2, 3, 4)
        timestamp = time.time()
        tile = Tile(index, b'a tile', 'text/plain', timestamp)
        self.cache.put('layer', tile)



if __name__ == '__main__':
    unittest.main()
