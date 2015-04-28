# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

import six

from stonemason.mason.mason import Mason
from stonemason.mason.mason import MasonTileVisitor, MasonMetaTileFarm
from stonemason.mason.metadata import Metadata
from stonemason.mason.mapbook import MapBook
from stonemason.mason.mapsheet import HybridMapSheet
from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTileIndex
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.tilestorage import MetaTileStorage
from .test_mapsheet import MockClusterStorage, MockMetaTileRenderer


class NullMapBook(MapBook):
    def __init__(self):
        MapBook.__init__(self, name='test', metadata=Metadata())


class TestMason(unittest.TestCase):
    def setUp(self):
        self.mason = Mason()

    def test_put_get_has_map_book(self):
        name = 'test'

        expected = NullMapBook()

        self.assertFalse(self.mason.has_map_book(name))

        self.mason.put_map_book(name, expected)
        self.assertTrue(self.mason.has_map_book(name))

        actually = self.mason.get_map_book(name)
        self.assertEqual(expected.name, actually.name)


class TestMasonTileAccessor(unittest.TestCase):
    def setUp(self):
        mason = Mason()

        self.name = 'test-name'
        self.tag = 'test-tag'

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        sheet = HybridMapSheet(
            self.tag,
            bundle,
            Pyramid(stride=2),
            MockClusterStorage(),
            MockMetaTileRenderer())

        book = MapBook(self.name, Metadata())
        book[sheet.tag] = sheet

        mason.put_map_book(book.name, book)

        self.accessor = MasonTileVisitor(mason)

    def test_get_tile(self):
        tile = self.accessor.get_tile(self.name, self.tag, 1, 0, 0)

        index = TileIndex(1, 0, 0)

        expected = Tile(index=index, data=six.b('A tile'))
        self.assertEqual(expected.index, tile.index)
        self.assertEqual(expected.data, tile.data)


class MockMetaTileStorage(MetaTileStorage):
    def __init__(self):
        self._storage = dict()

    @property
    def levels(self):
        return [1]

    @property
    def stride(self):
        return 1

    def put(self, metatile):
        self._storage[metatile.index] = metatile

    def get(self, index):
        return self._storage.get(index)


class TestMasonMetatileRenderer(unittest.TestCase):
    def setUp(self):
        mason = Mason()

        self.name = 'test-name'
        self.tag = 'test-tag'

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        self.storage = MockClusterStorage()
        sheet = HybridMapSheet(
            self.tag, bundle, Pyramid(stride=2),
            self.storage, MockMetaTileRenderer())

        book = MapBook(self.name, Metadata())
        book[sheet.tag]= sheet

        mason.put_map_book(book.name, book)

        self.renderer = MasonMetaTileFarm(mason)

    def test_render_metatile(self):
        self.renderer.render_metatile(self.name, self.tag, 1, 0, 0, 2)

        meta_index = MetaTileIndex(1, 0, 0, stride=2)
        cluster = self.storage.get(meta_index)

        self.assertEqual(len(cluster.tiles), 4)
