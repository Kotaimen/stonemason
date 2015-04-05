# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/4/15'

import six
import unittest

from stonemason.pyramid import MetaTileIndex
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
