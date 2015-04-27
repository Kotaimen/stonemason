# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.mason.metadata import Metadata
from stonemason.mason.mapbook import MapBook
from stonemason.mason.mapsheet import MapSheet


class MockMapSheet(MapSheet):
    def __init__(self, tag):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()
        MapSheet.__init__(self, tag, bundle, pyramid)

    def get_metatile(self, meta_index):
        return None

    def get_tilecluster(self, meta_index):
        return None

    def render_metatile(self, meta_index):
        return None


class TestMapBook(unittest.TestCase):
    def setUp(self):
        self.map_book = MapBook(name='test', metadata=Metadata())

    def test_name(self):
        self.assertEqual('test', self.map_book.name)

    def test_metadata(self):
        self.assertEqual(Metadata(), self.map_book.metadata)

    def test_put_get_has_map_sheet(self):
        tag = '2x.png'

        expected = MockMapSheet(tag)

        self.assertFalse(self.map_book.has_map_sheet(tag))

        self.map_book.put_map_sheet(expected.tag, expected)
        self.assertTrue(self.map_book.has_map_sheet(tag))

        actually = self.map_book.get_map_sheet(tag)
        self.assertEqual(expected.tag, actually.tag)

