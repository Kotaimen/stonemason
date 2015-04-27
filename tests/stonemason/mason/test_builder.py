# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

import shutil
import tempfile
import unittest

import moto
import boto

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import MapType, TileFormat
from stonemason.mason.metadata import Metadata
from stonemason.mason.builder import MapBookBuilder, MapSheetBuilder
from stonemason.tilestorage import ClusterStorage
from stonemason.renderer import MasonRenderer


class TestMapSheetBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = MapSheetBuilder()

    def test_build_default(self):
        sheet = self.builder.build()
        self.assertEqual('', sheet.tag)

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
        sheet = self.builder.build()

        self.assertIsInstance(sheet._storage, ClusterStorage)

    def test_build_disk_storage(self):
        root = tempfile.mkdtemp()
        storage_config = {
            'prototype': 'disk',
            'root': root
        }

        self.builder.build_storage(**storage_config)
        sheet = self.builder.build()

        self.assertIsInstance(sheet._storage, ClusterStorage)

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
            sheet = self.builder.build()

            self.assertIsInstance(sheet._storage, ClusterStorage)

    def test_build_renderer(self):
        renderer_config = {
            'prototype': 'image',
            'layers': {
                'root': {
                    'prototype': 'pil.black'
                }
            }
        }
        self.builder.build_renderer(**renderer_config)
        sheet = self.builder.build()

        self.assertIsInstance(sheet._renderer, MasonRenderer)


class TestMapBookBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = MapBookBuilder()

    def test_build_default(self):
        map_book = self.builder.build()
        self.assertEqual('', map_book.name)
        self.assertEqual(Metadata(), map_book.metadata)

    def test_build_name(self):
        self.builder.build_name('test')
        map_book = self.builder.build()
        self.assertEqual('test', map_book.name)

    def test_build_metadata(self):
        self.builder.build_metadata(title='test')
        map_book = self.builder.build()
        self.assertEqual('test', map_book.metadata.title)

