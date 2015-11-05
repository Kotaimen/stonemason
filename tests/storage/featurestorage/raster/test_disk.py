# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/3/15'

import os
import tempfile
import unittest
import shutil

from osgeo import gdal, osr

from stonemason.storage.featurestorage import ElevationDiskStorage

from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


class TestDiskRasterFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

        # create raster feature
        self.test_key = os.path.join(self.root, 'raster/fujisan_5m.tif')
        shutil.copytree(
            os.path.join(DATA_DIRECTORY, 'raster'),
            os.path.join(self.root, 'raster'))

    def tearDown(self):
        if os.path.exists(self.root):
            shutil.rmtree(self.root)

    def test_basic(self):
        storage = ElevationDiskStorage(
            root=self.root,
            index=os.path.join(self.root, 'raster/index_5m.shp'))

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        storage.delete(test_key)
        self.assertIsNone(storage.get(test_key))
        self.assertFalse(storage.has(test_key))

        storage.close()

    def test_intersection(self):
        storage = ElevationDiskStorage(
            root=self.root,
            index=os.path.join(self.root, 'raster/index_5m.shp'))

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        array = storage.intersection(test_envelope, crs='EPSG:4326',
                                     size=(256, 256))
        self.assertEqual(array.shape, (1, 256, 256))
