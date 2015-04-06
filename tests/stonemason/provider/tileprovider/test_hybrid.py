# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

import os
import io
import six
import unittest

from PIL import Image

from stonemason.pyramid import Pyramid, Tile, TileIndex, MetaTileIndex, MetaTile
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer.tilerenderer import MetaTileRenderer
from stonemason.provider.tilestorage import ClusterStorage, TileCluster
from stonemason.provider.tileprovider import RendererTileProvider
from stonemason.provider.tileprovider import StorageTileProvider
from stonemason.provider.tileprovider import HybridTileProvider

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


class TestHybridTileProviderWithDummy(unittest.TestCase):
    def setUp(self):
        maptype = MapType()
        tileformat = TileFormat('PNG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid(stride=2)

        renderer = DummyMetaTileRenderer()
        storage = DummyClusterStorage()

        self._provider = HybridTileProvider(bundle, pyramid, storage, renderer)

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(1, 0, 0, 2)

        # storage hit
        cluster = self._provider.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            self.assertEqual(six.b('A tile'), tile.data)

        meta_index = MetaTileIndex(2, 0, 0, 2)

        # renderer hit
        cluster = self._provider.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(1, 0, 0, 2)

        # storage miss (cluster storage does not support rendering metatile)
        metatile = self._provider.get_metatile(meta_index)
        self.assertIsNone(metatile)

        # renderer hit
        meta_index = MetaTileIndex(2, 0, 0, 2)

        metatile = self._provider.get_metatile(meta_index)
        grid_image = Image.open(io.BytesIO(metatile.data))
        self.assertEqual((1024, 1024), grid_image.size)
