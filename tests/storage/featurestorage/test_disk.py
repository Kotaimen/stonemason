# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/3/15'

import os
import tempfile
import unittest
import shutil

from osgeo import gdal, osr

from stonemason.storage.featurestorage import DiskRasterFeatureStorage

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

    def test_crs(self):
        storage = DiskRasterFeatureStorage(
            root=self.root,
            index_filename=os.path.join(self.root, 'raster/index_5m.shp'))

        crs = osr.SpatialReference()
        crs.ImportFromEPSG(4326)

        self.assertTrue(crs.IsSame(storage.crs))

    def test_envelope(self):
        storage = DiskRasterFeatureStorage(
            root=self.root,
            index_filename=os.path.join(self.root, 'raster/index_5m.shp'))

        envelope = (138.695869, 35.33096, 138.765564, 35.398994)
        self.assertEqual(envelope, storage.envelope)


    def test_basic(self):
        storage = DiskRasterFeatureStorage(
            root=self.root,
            index_filename=os.path.join(self.root, 'raster/index_5m.shp'))

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        storage.delete(test_key)
        self.assertIsNone(storage.get(test_key))
        self.assertFalse(storage.has(test_key))

        storage.close()

    def test_query(self):
        storage = DiskRasterFeatureStorage(
            root=self.root,
            index_filename=os.path.join(self.root, 'raster/index_5m.shp'))

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        for raster_key in storage.query(test_envelope, crs='EPSG:4326'):
            raster = storage.get(raster_key)

            self.assertEqual(self.test_key, raster_key)
            self.assertIsInstance(raster, gdal.Dataset)
