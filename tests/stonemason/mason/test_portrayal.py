# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.mason_.metadata import Metadata
from stonemason.mason_.portrayal import Portrayal
from stonemason.mason_.tilematrix import NullTileMatrix


class TestPortrayal(unittest.TestCase):
    def setUp(self):
        self.bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        self.portrayal = Portrayal(
            name='test', metadata=Metadata(), bundle=self.bundle,
            pyramid=Pyramid())

    def test_name(self):
        self.assertEqual('test', self.portrayal.name)

    def test_metadata(self):
        self.assertEqual(Metadata(), self.portrayal.metadata)

    def test_bundle(self):
        self.assertEqual(self.bundle, self.portrayal.bundle)

    def test_pyramid(self):
        self.assertEqual(Pyramid(), self.portrayal.pyramid)

    def test_put_get_has_tilematrix(self):
        tag = '2x.png'

        expected = NullTileMatrix(tag)

        self.assertFalse(self.portrayal.has_tilematrix(tag))

        self.portrayal.put_tilematrix(expected.tag, expected)
        self.assertTrue(self.portrayal.has_tilematrix(tag))

        actually = self.portrayal.get_tilematrix(tag)
        self.assertEqual(expected.tag, actually.tag)

