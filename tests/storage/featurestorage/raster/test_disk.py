# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/3/15'

import os
import tempfile
import unittest
import shutil
from osgeo import gdal
from stonemason.storage.featurestorage import create_feature_storage, \
    ReadOnlyFeatureStorage
from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


class TestDiskRasterFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

        # create raster feature
        self.test_key = 'fujisan_5m.tif'
        shutil.copytree(
            os.path.join(DATA_DIRECTORY, 'raster'),
            os.path.join(self.root, 'raster'))

    def tearDown(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    def test_basic(self):
        conn_string = 'raster+disk://%s?indexname=%s' % (
            os.path.join(self.root, 'raster'), 'index_5m.shp')
        storage = create_feature_storage(conn_string)

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        self.assertRaises(ReadOnlyFeatureStorage, storage.put, test_key, None)
        self.assertRaises(ReadOnlyFeatureStorage, storage.delete, test_key)

        storage.close()

    def test_intersection(self):
        conn_string = 'raster+disk://%s?indexname=%s' % (
            os.path.join(self.root, 'raster'), 'index_5m.shp')
        storage = create_feature_storage(conn_string)

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        expected_key = storage.intersection(test_envelope)
        self.assertEqual(expected_key, [self.test_key])
