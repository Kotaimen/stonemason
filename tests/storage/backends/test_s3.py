# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/27/15'

import unittest
import six
import moto
import boto3
from stonemason.storage.backends.s3 import S3Storage, S3HttpStorage

TEST_BUCKET_NAME = 'tilestorage'

class TestS3Storage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3')
        s3.Bucket(TEST_BUCKET_NAME).create()

        self.storage = S3Storage(bucket=TEST_BUCKET_NAME)

    def test_exists(self):
        test_key = 'test_key'
        test_blob = six.b('test_blob')
        test_metadata = dict(mimetype='test')

        self.storage.store(test_key, test_blob, test_metadata)

        self.assertTrue(self.storage.exists(test_key))
        self.assertFalse(self.storage.exists(test_key + 'nonexist'))

    def test_store(self):
        test_key = 'test_key'
        test_blob = six.b('test_blob')
        test_metadata = dict()

        self.storage.store(test_key, test_blob, test_metadata)
        blob, metadata = self.storage.retrieve(test_key)

        self.assertEqual(test_blob, blob)
        self.assertIn('LastModified', metadata)

    def test_retrieve(self):
        test_key = 'test_key'
        test_blob = six.b('test_blob')
        test_metadata = dict(test_meta='test_value')

        self.storage.store(test_key, test_blob, test_metadata)
        blob, metadata = self.storage.retrieve(test_key)

        self.assertEqual(test_blob, blob)
        self.assertIn('LastModified', metadata)
        self.assertIn('test_meta', metadata)
        self.assertEqual('test_value', metadata['test_meta'])

    def test_retire(self):
        test_key = 'test_key'
        test_blob = six.b('test_blob')
        test_metadata = dict()

        self.storage.store(test_key, test_blob, test_metadata)

        self.assertTrue(self.storage.exists(test_key))

        self.storage.retire(test_key)

        self.assertFalse(self.storage.exists(test_key))

    def tearDown(self):
        self.storage.close()
        self.mock.stop()


class TestS3HttpStorage(TestS3Storage):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3')
        s3.Bucket(TEST_BUCKET_NAME).create()

        self.storage = S3HttpStorage(bucket=TEST_BUCKET_NAME)
