# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import unittest
import moto
import boto3

from osgeo import gdal

from stonemason.storage.featurestorage import ElevationS3Storage

from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


class TestS3RasterFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3', region_name='us-east-1')
        s3.Bucket(TEST_BUCKET_NAME).create()

        self.basedir = os.path.join(DATA_DIRECTORY, 'raster')
        for _, _, filenames in os.walk(self.basedir):
            for filename in filenames:
                s3.Object(TEST_BUCKET_NAME, filename).upload_file(
                    os.path.join(self.basedir, filename))

        self.test_key = 'fujisan_5m.tif'

    def tearDown(self):
        self.mock.stop()

    def test_basic(self):
        storage = ElevationS3Storage(
            bucket=TEST_BUCKET_NAME,
            index='index_5m.shp')

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        storage.delete(test_key)
        self.assertIsNone(storage.get(test_key))
        self.assertFalse(storage.has(test_key))

        storage.close()

    def test_intersection(self):
        storage = ElevationS3Storage(
            bucket=TEST_BUCKET_NAME,
            index='index_5m.shp')

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        array = storage.intersection(test_envelope, crs='EPSG:4326', size=(256, 256))
        self.assertEqual(array.shape, (1, 256, 256))
