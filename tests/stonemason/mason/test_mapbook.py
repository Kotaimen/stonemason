# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.mason.metadata import Metadata
from stonemason.mason.mapbook import Mapbook
from stonemason.mason.mapsheet import MapSheet


class MockMapSheet(MapSheet):
    @property
    def storage(self):
        return None

    @property
    def renderer(self):
        return None

    def get_metatile(self, bundle, pyramid, meta_index):
        return None

    def get_tilecluster(self, bundle, pyramid, meta_index):
        return None

    def render_metatile(self, bundle, pyramid, meta_index):
        return None


class TestPortrayal(unittest.TestCase):
    def setUp(self):
        self.bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        self.portrayal = Mapbook(
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

        expected = MockMapSheet(tag)

        self.assertFalse(self.portrayal.has_schema(tag))

        self.portrayal.put_schema(expected.tag, expected)
        self.assertTrue(self.portrayal.has_schema(tag))

        actually = self.portrayal.get_schema(tag)
        self.assertEqual(expected.tag, actually.tag)

