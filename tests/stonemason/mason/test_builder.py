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
from stonemason.mason.builder import PortrayalBuilder, SchemaBuilder
from stonemason.tilestorage import ClusterStorage
from stonemason.renderer.tilerenderer import MetaTileRenderer
from tests import skipUnlessHasGDAL


class TestSchemaBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = SchemaBuilder()

    def test_build_default(self):
        schema = self.builder.build()
        self.assertEqual('', schema.tag)

    def test_build_pyramid(self):
        self.builder.build_pyramid(stride=2)
        self.assertEqual(Pyramid(stride=2), self.builder._pyramid)

    def test_build_map_type(self):
        self.builder.build_map_type('image')
        self.assertEqual(MapType('image'), self.builder._map_type)

    def test_build_tile_format(self):
        self.builder.build_tile_format(format='JPEG')
        self.assertEqual(TileFormat('JPEG'), self.builder._tile_format)

    def test_build_null_storage(self):
        storage_config = {
            'prototype': 'null',
        }

        self.builder.build_storage(**storage_config)
        schema = self.builder.build()

        self.assertIsInstance(schema._storage, ClusterStorage)

    def test_build_disk_storage(self):
        root = tempfile.mkdtemp()
        storage_config = {
            'prototype': 'disk',
            'root': root
        }

        self.builder.build_storage(**storage_config)
        schema = self.builder.build()

        self.assertIsInstance(schema._storage, ClusterStorage)

        shutil.rmtree(root, ignore_errors=True)

    def test_build_s3_storage(self):
        with moto.mock_s3():
            self.conn = boto.connect_s3()
            self.conn.create_bucket('test_storage')

            storage_config = {
                'prototype': 's3',
                'bucket': 'test_storage',
                'prefix': 'test_layer',
            }

            self.builder.build_storage(**storage_config)
            schema = self.builder.build()

            self.assertIsInstance(schema._storage, ClusterStorage)

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
        schema = self.builder.build()

        self.assertIsInstance(schema._renderer, MetaTileRenderer)


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

