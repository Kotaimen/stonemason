# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import unittest
import moto
import boto3
from osgeo import gdal
from stonemason.storage.featurestorage import create_feature_storage, \
    ReadOnlyFeatureStorage
from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


@unittest.skip
class TestS3RasterFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3')
        s3.Bucket(TEST_BUCKET_NAME).create()

        self.basedir = os.path.join(DATA_DIRECTORY, 'raster')
        self.prefix = 'prefix'
        for _, _, filenames in os.walk(self.basedir):
            for filename in filenames:
                key = '/'.join([self.prefix, filename])
                s3.Object(TEST_BUCKET_NAME, key).upload_file(
                    os.path.join(self.basedir, filename))

        self.test_key = 'fujisan_5m.tif'

    def tearDown(self):
        self.mock.stop()

    def test_basic(self):
        conn_string = 'raster+s3://%s?indexname=%s' % (
            '/'.join([TEST_BUCKET_NAME, self.prefix]), 'index_5m.shp')
        storage = create_feature_storage(conn_string)

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        self.assertRaises(ReadOnlyFeatureStorage, storage.put, test_key, None)
        self.assertRaises(ReadOnlyFeatureStorage, storage.delete, test_key)

        storage.close()

    def test_intersection(self):
        conn_string = 'raster+s3://%s?indexname=%s' % (
            '/'.join([TEST_BUCKET_NAME, self.prefix]), 'index_5m.shp')
        storage = create_feature_storage(conn_string)

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        expected_key = storage.intersection(test_envelope)
        self.assertEqual(expected_key, [self.test_key])
