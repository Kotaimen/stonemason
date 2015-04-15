# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

import shutil
import tempfile
import unittest

import moto
import boto

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.mason.metadata import Metadata
from stonemason.mason.builder import PortrayalBuilder, SchemaBuilder, \
    create_cluster_storage, create_metatile_renderer
from stonemason.tilestorage import ClusterStorage
from stonemason.renderer.tilerenderer import MetaTileRenderer
from tests import skipUnlessHasGDAL


class TestCreateClusterStorage(unittest.TestCase):
    def test_build_null_storage(self):
        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        storage = create_cluster_storage(bundle, pyramid)

        self.assertIsInstance(storage, ClusterStorage)

    def test_build_disk_storage(self):
        root = tempfile.mkdtemp()

        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        storage_config = {
            'prototype': 'disk',
            'root': root
        }

        storage = create_cluster_storage(bundle, pyramid, **storage_config)

        self.assertIsInstance(storage, ClusterStorage)

        shutil.rmtree(root, ignore_errors=True)

    def test_build_s3_storage(self):
        with moto.mock_s3():
            self.conn = boto.connect_s3()
            self.conn.create_bucket('test_storage')

            maptype = MapType('image')
            tileformat = TileFormat('JPEG')
            bundle = FormatBundle(maptype, tileformat)

            pyramid = Pyramid()

            storage_config = {
                'prototype': 's3',
                'bucket': 'test_storage',
                'prefix': 'test_layer',
            }

            storage = create_cluster_storage(bundle, pyramid, **storage_config)

            self.assertIsInstance(storage, ClusterStorage)


class TestCreateMetaTileRenderer(unittest.TestCase):
    @skipUnlessHasGDAL()
    def test_build_image_renderer(self):
        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        renderer_config = {
            'prototype': 'image',
            'layers': {
                'root': {
                    'type': 'dummy'
                }
            }
        }

        renderer = create_metatile_renderer(bundle, pyramid, **renderer_config)

        self.assertIsInstance(renderer, MetaTileRenderer)


class TestTileMatrixBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = SchemaBuilder()

    def test_build_default(self):
        tile_matrix = self.builder.build()
        self.assertEqual('.png', tile_matrix.tag)
        self.assertEqual(None, tile_matrix.get_tilecluster(None, None, None))
        self.assertEqual(None, tile_matrix.get_metatile(None, None, None))

    def test_build_pyramid(self):
        self.builder.build_pyramid(stride=2)
        self.assertEqual(Pyramid(stride=2), self.builder._pyramid)

    def test_build_map_type(self):
        self.builder.build_map_type('image')
        self.assertEqual(MapType('image'), self.builder._map_type)

    def test_build_tile_format(self):
        self.builder.build_tile_format(format='JPEG')
        self.assertEqual(TileFormat('JPEG'), self.builder._tile_format)

    def test_build_storage(self):
        root = tempfile.mkdtemp()
        storage_config = {
            'prototype': 'disk',
            'root': root
        }

        self.builder.build_storage(**storage_config)
        tile_matrix = self.builder.build()

        self.assertIsInstance(tile_matrix._storage, ClusterStorage)

        shutil.rmtree(root, ignore_errors=True)

    @skipUnlessHasGDAL()
    def test_build_renderer(self):
        renderer_config = {
            'prototype': 'image',
            'layers': {
                'root': {
                    'type': 'dummy'
                }
            }
        }
        self.builder.build_renderer(**renderer_config)
        tile_matrix = self.builder.build()

        self.assertIsInstance(tile_matrix._renderer, MetaTileRenderer)


class TestPortrayalBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = PortrayalBuilder()

    def test_build_default(self):
        portrayal = self.builder.build()
        self.assertEqual('', portrayal.name)
        self.assertEqual(Metadata(), portrayal.metadata)
        self.assertEqual(MapType('image'), portrayal.bundle.map_type)
        self.assertEqual(TileFormat('PNG'), portrayal.bundle.tile_format)
        self.assertEqual(Pyramid(), portrayal.pyramid)

    def test_build_name(self):
        self.builder.build_name('test')
        portrayal = self.builder.build()
        self.assertEqual('test', portrayal.name)

    def test_build_metadata(self):
        self.builder.build_metadata(title='test')
        portrayal = self.builder.build()
        self.assertEqual('test', portrayal.metadata.title)

    def test_build_pyramid(self):
        self.builder.build_pyramid(stride=2)
        portrayal = self.builder.build()
        self.assertEqual(2, portrayal.pyramid.stride)

    def test_build_map_type(self):
        self.builder.build_map_type('image')
        portrayal = self.builder.build()
        self.assertEqual(MapType('image'), portrayal.bundle.map_type)

    def test_build_tile_format(self):
        self.builder.build_tile_format(format='JPEG')
        portrayal = self.builder.build()
        self.assertEqual(TileFormat('JPEG'), portrayal.bundle.tile_format)

