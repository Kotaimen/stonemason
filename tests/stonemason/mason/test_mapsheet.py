# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import os
import io
import unittest

import six
from PIL import Image

from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTile, MetaTileIndex
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer import MasonRenderer, ImageFeature
from stonemason.tilestorage import ClusterStorage, TileCluster
from stonemason.mason.mapsheet import HybridMapSheet
from tests import DATA_DIRECTORY
from tests import skipUnlessHasGDAL


class MockMetaTileRenderer(MasonRenderer):
    def __init__(self):
        MasonRenderer.__init__(self, {})

    def render(self, context):
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop', 'grid.png')
        image_data = Image.open(grid_image)
        return ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=image_data)


class MockClusterStorage(ClusterStorage):
    @property
    def levels(self):
        raise NotImplementedError

    @property
    def stride(self):
        return 2

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


class TestHybridMapSheet(unittest.TestCase):
    def setUp(self):
        storage = MockClusterStorage()
        renderer = MockMetaTileRenderer()

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        self.matrix = HybridMapSheet('test', bundle, pyramid, storage, renderer)

    @skipUnlessHasGDAL()
    def test_get_tilecluster(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(1, 0, 0, pyramid.stride)

        # storage hit
        cluster = self.matrix.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            self.assertEqual(six.b('A tile'), tile.data)

        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        # renderer hit
        cluster = self.matrix.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

    @skipUnlessHasGDAL()
    def test_get_metatile(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(1, 0, 0, pyramid.stride)

        # storage miss (cluster storage does not support rendering metatile)
        metatile = self.matrix.get_metatile(meta_index)
        # self.assertIsNone(metatile)

        # renderer hit
        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        metatile = self.matrix.get_metatile(meta_index)
        grid_image = Image.open(io.BytesIO(metatile.data))
        self.assertEqual((1024, 1024), grid_image.size)

