# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/18/15'

import unittest
import hashlib

from stonemason.pyramid import MetaTile, MetaTileIndex, TileIndex


class TestMetaTileIndex(unittest.TestCase):
    def test_init(self):
        index1 = MetaTileIndex()
        self.assertEqual(index1.z, 0)
        self.assertEqual(index1.x, 0)
        self.assertEqual(index1.y, 0)
        self.assertEqual(index1.stride, 1)

        index2 = MetaTileIndex(4, 4, 8, 4)
        self.assertEqual(index2.z, 4)
        self.assertEqual(index2.x, 4)
        self.assertEqual(index2.y, 8)
        self.assertEqual(index2.stride, 4)

    def test_snap_coord(self):
        index1 = MetaTileIndex(4, 5, 9, 4)
        self.assertEqual(index1.z, 4)
        self.assertEqual(index1.x, 4)
        self.assertEqual(index1.y, 8)
        self.assertEqual(index1.stride, 4)

        index2 = MetaTileIndex(6, 33, 7, 8)
        self.assertEqual(index2.z, 6)
        self.assertEqual(index2.x, 32)
        self.assertEqual(index2.y, 0)
        self.assertEqual(index2.stride, 8)

    def test_adjust_stride(self):
        index1 = MetaTileIndex(0, 0, 0, 4)
        self.assertEqual(index1.z, 0)
        self.assertEqual(index1.x, 0)
        self.assertEqual(index1.y, 0)
        self.assertEqual(index1.stride, 1)

        index2 = MetaTileIndex(3, 1, 2, 16)
        self.assertEqual(index2.z, 3)
        self.assertEqual(index2.x, 0)
        self.assertEqual(index2.y, 0)
        self.assertEqual(index2.stride, 8)

    def test_to_tileindex(self):
        index1 = MetaTileIndex(3, 1, 2, 4)
        index2 = index1.to_tile_index()
        self.assertEqual(index2, TileIndex(1, 0, 0))

    def test_repr(self):
        index = MetaTileIndex(2, 2, 3, 8)
        self.assertEqual(str(index), 'MetaTileIndex(2/0/0@4)')

    def test_fission(self):
        index1 = MetaTileIndex(2, 0, 0, 2)
        self.assertSetEqual(
            set(index1.fission()),
            set([TileIndex(2, 0, 0),
                 TileIndex(2, 0, 1),
                 TileIndex(2, 1, 0),
                 TileIndex(2, 1, 1), ]))


class TestMetaTile(unittest.TestCase):
    def test_init(self):
        meta1 = MetaTile()
        self.assertEqual(meta1.index, MetaTileIndex(0, 0, 0, 1))
        self.assertEqual(meta1.data, b'')
        self.assertEqual(meta1.mimetype, 'application/data')
        self.assertGreater(meta1.mtime, 0)
        self.assertEqual(meta1.etag, hashlib.md5(b'').hexdigest())
        self.assertEqual(meta1.buffer, 0)

        meta2 = MetaTile(MetaTileIndex(4, 15, 8, 4),
                         b'a meta tile', 'text/plain',
                         mtime=1234.5, etag='abcde', buffer=16)
        self.assertEqual(meta2.index, (4, 12, 8, 4))
        self.assertEqual(meta2.data, b'a meta tile')
        self.assertEqual(meta2.mimetype, 'text/plain')
        self.assertEqual(meta2.mtime, 1234.5)
        self.assertEqual(meta2.etag, 'abcde')
        self.assertEqual(meta2.buffer, 16)

    def test_repr(self):
        index = MetaTile(MetaTileIndex(2, 2, 3, 8))
        self.assertEqual(str(index), 'MetaTile(2/0/0@4)')


    if __name__ == '__main__':
        unittest.main()
