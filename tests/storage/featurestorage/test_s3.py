# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import unittest
import moto
import boto3

from osgeo import osr, gdal

from stonemason.storage.featurestorage import S3RasterFeatureStorage

from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


class TestS3RasterFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3')
        s3.Bucket(TEST_BUCKET_NAME).create()

        self.basedir = os.path.join(DATA_DIRECTORY, 'raster')
        for _, _, filenames in os.walk(self.basedir):
            for filename in filenames:
                s3.Object(TEST_BUCKET_NAME, filename).upload_file(
                    os.path.join(self.basedir, filename))

        self.test_key = 'fujisan_5m.tif'

    def tearDown(self):
        self.mock.stop()

    def test_crs(self):
        storage = S3RasterFeatureStorage(
            bucket=TEST_BUCKET_NAME,
            index_filename='index_5m.shp')

        crs = osr.SpatialReference()
        crs.ImportFromEPSG(4326)

        self.assertTrue(crs.IsSame(storage.crs))

    def test_envelope(self):
        storage = S3RasterFeatureStorage(
            bucket=TEST_BUCKET_NAME,
            index_filename='index_5m.shp')

        envelope = (138.695869, 35.33096, 138.765564, 35.398994)
        self.assertEqual(envelope, storage.envelope)

    def test_basic(self):
        storage = S3RasterFeatureStorage(
            bucket=TEST_BUCKET_NAME,
            index_filename='index_5m.shp')

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        storage.delete(test_key)
        self.assertIsNone(storage.get(test_key))
        self.assertFalse(storage.has(test_key))

        storage.close()

    def test_query(self):
        storage = S3RasterFeatureStorage(
            bucket=TEST_BUCKET_NAME,
            index_filename='index_5m.shp')

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        for raster_key in storage.query(test_envelope, crs='EPSG:4326'):
            raster = storage.get(raster_key)

            self.assertEqual(self.test_key, raster_key)
            self.assertIsInstance(raster, gdal.Dataset)
