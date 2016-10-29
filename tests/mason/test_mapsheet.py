# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import io
import unittest

from PIL import Image

from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTile, \
    MetaTileIndex, TileCluster
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer import MasonRenderer
from stonemason.renderer.cartographer import ImageFeature
from stonemason.storage import ClusterStorage, MetaTileStorageConcept
from stonemason.mason.mapsheet import ClusterMapSheet, MetaTileMapSheet

from tests import skipUnlessHasGDAL


class MockMetaTileRenderer(MasonRenderer):
    def __init__(self):
        MasonRenderer.__init__(self, {})

    def render(self, context):
        image = Image.new('RGB', (512, 512), color='#fff')

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=image)
        return feature


def mock_image_data(mode, size, color):
    image = Image.new(mode, size, color=color)
    bytes = io.BytesIO()
    image.save(bytes, 'png')
    image_data = bytes.getvalue()
    return image_data


def mock_tilecluster():
    index = MetaTileIndex(1, 0, 0, 2)

    image_data = mock_image_data('RGB', (256, 256), '#000')

    tiles = [
        Tile(index=TileIndex(1, 0, 0), data=image_data),
        Tile(index=TileIndex(1, 0, 1), data=image_data),
        Tile(index=TileIndex(1, 1, 0), data=image_data),
        Tile(index=TileIndex(1, 1, 1), data=image_data)
    ]

    cluster = TileCluster(index=index, tiles=tiles)
    return cluster


class MockClusterStorage(ClusterStorage):
    def __init__(self, bundle):
        self._storage = dict()
        self._bundle = bundle

        cluster = mock_tilecluster()

        self._storage[cluster.index] = cluster

    @property
    def stride(self):
        return 2

    def get(self, index):
        return self._storage.get(index)

    def put(self, metatile):
        cluster = TileCluster.from_metatile(metatile, self._bundle.writer)
        self._storage[metatile.index] = cluster


def mock_metatile():
    index = MetaTileIndex(1, 0, 0, 2)

    image_data = mock_image_data('RGB', (512, 512), '#000')
    meta_tile = MetaTile(index=index, data=image_data)

    return meta_tile


class MockMetaTileStorage(MetaTileStorageConcept):
    def __init__(self, bundle):
        self._storage = dict()
        self._bundle = bundle

        meta_tile = mock_metatile()

        self._storage[meta_tile.index] = meta_tile

    @property
    def stride(self):
        return 2

    def has(self, index):
        return index in self._storage

    def get(self, index):
        return self._storage.get(index)

    def put(self, metatile):
        self._storage[metatile.index] = metatile

    @skipUnlessHasGDAL()
    def test_get_tilecluster(self):
        # storage hit
        meta_index = MetaTileIndex(1, 0, 0, 2)
        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#000')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)

        # renderer hit
        meta_index = MetaTileIndex(2, 0, 0, 2)
        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#fff')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)

    @skipUnlessHasGDAL()
    def test_render_metatile(self):
        meta_index = MetaTileIndex(2, 0, 0, 2)
        self.mapsheet.render_metatile(meta_index)

        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#fff')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)


class MapSheetTestCase(object):
    @skipUnlessHasGDAL()
    def test_get_tilecluster(self):
        # storage hit
        meta_index = MetaTileIndex(1, 0, 0, 2)
        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#000')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)

        # renderer hit
        meta_index = MetaTileIndex(2, 0, 0, 2)
        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#fff')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)

    @skipUnlessHasGDAL()
    def test_render_metatile(self):
        meta_index = MetaTileIndex(2, 0, 0, 2)
        self.mapsheet.render_metatile(meta_index)

        cluster = self.mapsheet.get_tilecluster(meta_index)

        expected = mock_image_data('RGB', (256, 256), '#fff')

        for tile in cluster.tiles:
            self.assertEqual(expected, tile.data)


class TestMetatileMapSheet(unittest.TestCase, MapSheetTestCase):
    def setUp(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        storage = MockMetaTileStorage(bundle=bundle)

        renderer = MockMetaTileRenderer()

        self.mapsheet = MetaTileMapSheet(
            'test', bundle, pyramid, storage, renderer)


class TestClusterMapSheet(unittest.TestCase, MapSheetTestCase):
    def setUp(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        storage = MockClusterStorage(bundle=bundle)

        renderer = MockMetaTileRenderer()

        self.mapsheet = ClusterMapSheet(
            'test', bundle, pyramid, storage, renderer)
