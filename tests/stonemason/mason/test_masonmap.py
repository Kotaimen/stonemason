# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

import unittest

from stonemason.mason import MasonMap
from stonemason.provider.tileprovider import TileProvider, NullTileProvider


class TestMasonMap(unittest.TestCase):
    def setUp(self):
        self.mason_map = MasonMap(
            name='test',
            metadata={'version': '0.0.1'},
            provider=NullTileProvider())

    def test_name(self):
        self.assertEqual('test', self.mason_map.name)

    def test_metadata(self):
        self.assertEqual({'version': '0.0.1'}, self.mason_map.metadata)

    def test_provider(self):
        self.assertIsInstance(self.mason_map.provider, TileProvider)
