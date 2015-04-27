# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

import six

from stonemason.mason.mason import Mason
from stonemason.mason.mason import MasonTileVisitor, MasonMetaTileFarm
from stonemason.mason.metadata import Metadata
from stonemason.mason.mapbook import Mapbook
from stonemason.mason.mapsheet import HybridMapSheet
from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTileIndex
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.tilestorage import MetaTileStorage
from .test_mapsheet import DummyClusterStorage, DummyMetaTileRenderer


class NullPortrayal(Mapbook):
    def __init__(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        Mapbook.__init__(
            self,
            name='test',
            metadata=Metadata(),
            bundle=bundle,
            pyramid=Pyramid())


class TestMason(unittest.TestCase):
    def setUp(self):
        self.mason = Mason()

    def test_put_get_has_portrayal(self):
        name = 'test'

        expected = NullPortrayal()

        self.assertFalse(self.mason.has_portrayal(name))

        self.mason.put_portrayal(name, expected)
        self.assertTrue(self.mason.has_portrayal(name))

        actually = self.mason.get_portrayal(name)
        self.assertEqual(expected.name, actually.name)


class TestMasonTileAccessor(unittest.TestCase):
    def setUp(self):
        mason = Mason()

        self.name = 'test-name'
        self.tag = 'test-tag'

        tilematrix = HybridMapSheet(
            self.tag, DummyClusterStorage(), DummyMetaTileRenderer())

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        portrayal = Mapbook(self.name, Metadata(), bundle, Pyramid(stride=2))
        portrayal.put_schema(tilematrix.tag, tilematrix)

        mason.put_portrayal(portrayal.name, portrayal)

        self.accessor = MasonTileVisitor(mason)

    def test_get_tile(self):
        tile = self.accessor.get_tile(self.name, self.tag, 1, 0, 0)

        index = TileIndex(1, 0, 0)

        expected = Tile(index=index, data=six.b('A tile'))
        self.assertEqual(expected.index, tile.index)
        self.assertEqual(expected.data, tile.data)


class DummyMetaTileStorage(MetaTileStorage):
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

        self.storage = DummyClusterStorage()
        tilematrix = HybridMapSheet(
            self.tag, self.storage, DummyMetaTileRenderer())

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))

        portrayal = Mapbook(self.name, Metadata(), bundle, Pyramid(stride=2))
        portrayal.put_schema(tilematrix.tag, tilematrix)

        mason.put_portrayal(portrayal.name, portrayal)

        self.renderer = MasonMetaTileFarm(mason)

    def test_render_metatile(self):
        self.renderer.render_metatile(self.name, self.tag, 1, 0, 0, 2)

        meta_index = MetaTileIndex(1, 0, 0, stride=2)
        cluster = self.storage.get(meta_index)

        self.assertEqual(len(cluster.tiles), 4)
