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
    def __init__(self, bundle):
        self._storage = dict()
        self._bundle = bundle

        index = MetaTileIndex(1, 0, 0, 2)

        tiles = [
            Tile(index=TileIndex(1, 0, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 0, 1), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 0), data=six.b('A tile')),
            Tile(index=TileIndex(1, 1, 1), data=six.b('A tile'))
        ]

        cluster = TileCluster(index=index, tiles=tiles)

        self._storage[index] = cluster

    @property
    def levels(self):
        raise NotImplementedError

    @property
    def stride(self):
        return 2

    def get(self, index):
        try:
            return self._storage[index]
        except KeyError:
            return None

    def put(self, metatile):
        cluster = TileCluster.from_metatile(metatile, self._bundle.writer)
        self._storage[metatile.index] = cluster


class TestHybridMapSheet(unittest.TestCase):
    def setUp(self):

        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid()

        storage = MockClusterStorage(bundle=bundle)

        renderer = MockMetaTileRenderer()

        self.mapsheet = HybridMapSheet(
            'test', bundle, pyramid, storage, renderer)

    @skipUnlessHasGDAL()
    def test_get_tilecluster(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(1, 0, 0, pyramid.stride)

        # storage hit
        cluster = self.mapsheet.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            self.assertEqual(six.b('A tile'), tile.data)

        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        # renderer hit
        cluster = self.mapsheet.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

    @skipUnlessHasGDAL()
    def test_render_metatile(self):
        bundle = FormatBundle(MapType('image'), TileFormat('PNG'))
        pyramid = Pyramid(stride=2)

        meta_index = MetaTileIndex(2, 0, 0, pyramid.stride)

        self.mapsheet.render_metatile(meta_index)

        cluster = self.mapsheet.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

