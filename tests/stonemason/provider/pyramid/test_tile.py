# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/14/15'

import unittest
import hashlib

from stonemason.provider.pyramid import Tile, TileIndex


class TestTileIndex(unittest.TestCase):
    def test_init(self):
        index1 = TileIndex()
        self.assertEqual(index1.x, 0)
        self.assertEqual(index1.y, 0)
        self.assertEqual(index1.z, 0)
        index2 = TileIndex(2, 3, 4)
        self.assertEqual(index2.x, 3)
        self.assertEqual(index2.y, 4)
        self.assertEqual(index2.z, 2)

    def test_repr(self):
        index = TileIndex(2, 3, 4)
        self.assertEqual(str(index), 'TileIndex(2/3/4)')

    def test_serial(self):
        index = TileIndex(3, 4, 5)
        self.assertEqual(index.serial, 0xc00000000000023)

    def test_eq(self):
        index2 = TileIndex(4, 4, 5)
        index1 = TileIndex(3, 4, 5)
        index3 = TileIndex(3, 4, 5)
        self.assertNotEqual(index1, index2)
        self.assertEqual(index1, index3)
        self.assertEqual(index1, (3, 4, 5))

    def test_hash(self):
        index = TileIndex(3, 4, 5)
        self.assertEqual(hash(index), 0xc00000000000023)


class TestTile(unittest.TestCase):
    def test_init1(self):
        tile = Tile()
        self.assertEqual(tile.index, (0, 0, 0))
        self.assertEqual(tile.data, b'')
        self.assertEqual(tile.mimetype, 'application/data')
        self.assertGreater(tile.mtime, 0)
        self.assertEqual(tile.etag, hashlib.md5(b'').digest())

    def test_init2(self):
        tile = Tile(index=TileIndex(2, 3, 4),
                    data=b'a tile',
                    mimetype='text/plain',
                    mtime=1234.)
        self.assertEqual(tile.index, (2, 3, 4))
        self.assertEqual(tile.data, b'a tile')
        self.assertEqual(tile.mimetype, 'text/plain')
        self.assertGreater(tile.mtime, 0.)
        self.assertEqual(tile.etag, 'c37ee78cb8b04fa64e295342b3e229cd')

    def test_hash(self):
        tile = Tile(TileIndex(3, 4, 5))
        self.assertEqual(hash(tile), 0xc00000000000023)

    def test_repr(self):
        tile = Tile(TileIndex(3, 4, 5))
        self.assertEqual(str(tile), 'Tile(3/4/5)')


if __name__ == '__main__':
    unittest.main()
