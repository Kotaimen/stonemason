# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/28/15'

import os
import shutil
import unittest

import tempfile
import six

from stonemason.storage.backends.disk import DiskStorage

TEST_BUCKET_NAME = 'tilestorage'


class TestS3Storage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.storage = DiskStorage()

    def test_exists(self):
        test_key = os.path.join(self.root,'test_key')
        test_blob = six.b('test_blob')
        test_metadata = dict(mimetype='test')

        self.storage.store(test_key, test_blob, test_metadata)

        self.assertTrue(self.storage.exists(test_key))
        self.assertFalse(self.storage.exists(test_key + 'nonexist'))

    def test_store(self):
        test_key = os.path.join(self.root,'test_key')
        test_blob = six.b('test_blob')
        test_metadata = dict()

        self.storage.store(test_key, test_blob, test_metadata)
        blob, metadata = self.storage.retrieve(test_key)

        self.assertEqual(test_blob, blob)
        self.assertIn('LastModified', metadata)

    def test_retrieve(self):
        test_key = os.path.join(self.root,'test_key')
        test_blob = six.b('test_blob')
        test_metadata = dict(test_meta='test_value')

        self.storage.store(test_key, test_blob, test_metadata)
        blob, metadata = self.storage.retrieve(test_key)

        self.assertEqual(test_blob, blob)
        self.assertIn('LastModified', metadata)
        self.assertNotIn('test_meta', metadata)

    def test_retire(self):
        test_key = os.path.join(self.root,'test_key')
        test_blob = six.b('test_blob')
        test_metadata = dict()

        self.storage.store(test_key, test_blob, test_metadata)

        self.assertTrue(self.storage.exists(test_key))

        self.storage.retire(test_key)

        self.assertFalse(self.storage.exists(test_key))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
