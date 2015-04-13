# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/11/15'

import unittest
import os

from stonemason.pyramid import MetaTileIndex
from stonemason.service.renderman.walkers import CompleteWalker, TileListWalker

from tests import DATA_DIRECTORY


class TestPyramidWalker(unittest.TestCase):
    def setUp(self):
        self.tilelist1 = os.path.join(DATA_DIRECTORY, 'walkers',
                                      'tilelist1.csv')

    def test_complete_walker(self):
        walker = CompleteWalker([0, 1, 2], 2)
        indexes = list(walker)

        self.assertListEqual(indexes,
                             [MetaTileIndex(0, 0, 0, 1),
                              MetaTileIndex(1, 0, 0, 2),
                              MetaTileIndex(2, 0, 0, 2),
                              MetaTileIndex(2, 0, 2, 2),
                              MetaTileIndex(2, 2, 0, 2),
                              MetaTileIndex(2, 2, 2, 2)])

    def test_tilelist_walker(self):
        walker = TileListWalker([1, 2, 3], 2, self.tilelist1)
        indexes = list(walker)
        self.assertListEqual(indexes,
                             [MetaTileIndex(2, 0, 2, 2),
                              MetaTileIndex(3, 0, 4, 2),
                              MetaTileIndex(3, 0, 6, 2),
                              MetaTileIndex(3, 2, 4, 2),
                              MetaTileIndex(3, 2, 6, 2),
                              MetaTileIndex(2, 2, 2, 2),
                              MetaTileIndex(3, 4, 6, 2)])


if __name__ == '__main__':
    unittest.main()
