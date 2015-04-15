# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import os
import io
import unittest

import six
from PIL import Image

from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTile, MetaTileIndex
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer.tilerenderer import MetaTileRenderer
from stonemason.provider.tilestorage import ClusterStorage, TileCluster
from stonemason.mason.schema import HybridSchema, NullSchema

from tests import DATA_DIRECTORY


class DummyMetaTileRenderer(MetaTileRenderer):
    def render_metatile(self, meta_index):
        if meta_index != MetaTileIndex(2, 0, 0, 2):
            return None

        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop', 'grid.png')
        image_data = open(grid_image, mode='rb').read()
        return MetaTile(index=meta_index, data=image_data)


class DummyClusterStorage(ClusterStorage):
    def get(self, index):
        if index != MetaTileIndex(1, 0, 0, 2):
            return None

        tiles = [
            Tile(index=TileIndex(1, 0, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 0, 1), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 1), data=six.b('A tile'))
        ]
        return TileCluster(index=index, tiles=tiles)

    def put(self, metatile):
        pass


class TestHybridTileMatrix(unittest.TestCase):
    def setUp(self):
        storage = DummyClusterStorage()
        renderer = DummyMetaTileRenderer()

        self.matrix = HybridSchema('test', storage, renderer)

    def test_get_tilecluster(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(1, 0, 0, pyramid.stride)

        # storage hit
        cluster = self.matrix.get_tilecluster(bundle, pyramid, meta_index)
        for tile in cluster.tiles:
            self.assertEqual(six.b('A tile'), tile.data)

        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        # renderer hit
        cluster = self.matrix.get_tilecluster(bundle, pyramid, meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

    def test_get_metatile(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(1, 0, 0, pyramid.stride)

        # storage miss (cluster storage does not support rendering metatile)
        metatile = self.matrix.get_metatile(bundle, pyramid, meta_index)
        self.assertIsNone(metatile)

        # renderer hit
        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        metatile = self.matrix.get_metatile(bundle, pyramid, meta_index)
        grid_image = Image.open(io.BytesIO(metatile.data))
        self.assertEqual((1024, 1024), grid_image.size)


class TestNullTileMatrix(unittest.TestCase):
    def setUp(self):
        self.matrix = NullSchema()

    def test_get_tilecluster(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        meta_index = MetaTileIndex(2, 0, 0, 2)
        self.assertIsNone(
            self.matrix.get_tilecluster(bundle, pyramid, meta_index))

    def test_get_metatile(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        meta_index = MetaTileIndex(2, 0, 0, 2)
        self.assertIsNone(
            self.matrix.get_metatile(bundle, pyramid, meta_index))
