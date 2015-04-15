# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/29/15'

import os
import io
import unittest

from PIL import Image

from stonemason.pyramid import Pyramid, MetaTileIndex, MetaTile
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer.tilerenderer import NullMetaTileRenderer
from stonemason.renderer.tilerenderer import MetaTileRenderer
from stonemason.provider.tileprovider import RendererTileProvider
from tests import DATA_DIRECTORY


class DummyMetaTileRenderer(MetaTileRenderer):
    def render_metatile(self, meta_index):
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop', 'grid.png')
        image_data = open(grid_image, mode='rb').read()
        return MetaTile(index=meta_index, data=image_data)


class TestStorageProviderWithDummyStorage(unittest.TestCase):
    def setUp(self):
        maptype = MapType()
        tileformat = TileFormat('PNG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid(stride=2)

        renderer = DummyMetaTileRenderer()

        self._provider = RendererTileProvider(bundle, pyramid, renderer)

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(2, 0, 0, 2)

        cluster = self._provider.get_tilecluster(meta_index)
        for tile in cluster.tiles:
            grid_image = Image.open(io.BytesIO(tile.data))
            self.assertEqual((512, 512), grid_image.size)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(2, 0, 0, 2)

        metatile = self._provider.get_metatile(meta_index)

        grid_image = Image.open(io.BytesIO(metatile.data))

        self.assertEqual((1024, 1024), grid_image.size)


class TestStorageProviderWithNullStorage(unittest.TestCase):
    def setUp(self):
        maptype = MapType()
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        renderer = NullMetaTileRenderer()

        self._provider = RendererTileProvider(bundle, pyramid, renderer)

    def test_get_tilecluster(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        cluster = self._provider.get_tilecluster(meta_index)
        self.assertIsNone(cluster)

    def test_get_metatile(self):
        meta_index = MetaTileIndex(0, 0, 0, 1)

        metatile = self._provider.get_metatile(meta_index)
        self.assertIsNone(metatile)


