# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/30/15'

import unittest
import os

import moto
import boto, boto.s3

from stonemason.provider.pyramid import MetaTile, MetaTileIndex, Pyramid
from stonemason.provider.tilestorage import S3ClusterStorage, \
    S3MetaTileStorage, TileCluster, \
    InvalidMetaTile, InvalidMetaTileIndex, ReadonlyStorage

TEST_BUCKET_NAME = 'tilestorage'

from tests import DATA_DIRECTORY


class TestS3ClusterStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()
        self.conn = boto.connect_s3()
        self.conn.create_bucket(TEST_BUCKET_NAME)
        self.pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')

        self.metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                                 data=open(grid_image, 'rb').read(),
                                 mimetype='image/png')

    def test_basic(self):
        storage = S3ClusterStorage(bucket=TEST_BUCKET_NAME,
                                   prefix='testlayer',
                                   pyramid=self.pyramid,
                                   mimetype='image/png')
        storage.put(self.metatile)

        cluster = storage.get(self.metatile.index)
        self.assertIsInstance(cluster, TileCluster)

        tile = cluster.tiles[0]

        self.assertEqual(cluster.index, self.metatile.index)
        self.assertAlmostEqual(tile.mtime, self.metatile.mtime, 0)
        self.assertEqual(tile.mimetype, self.metatile.mimetype)


        storage.retire(self.metatile.index)
        self.assertIsNone(storage.get(self.metatile.index))
        storage.close()

    def test_keymode_simple(self):
        storage = S3ClusterStorage(bucket=TEST_BUCKET_NAME,
                                   prefix='testlayer',
                                   pyramid=self.pyramid,
                                   mimetype='image/png')
        storage.put(self.metatile)

        self.assertIsNotNone(self.conn.get_bucket(TEST_BUCKET_NAME).get_key(
            'testlayer/19/453824/212288/19-453824-212288@8.zip'))

    def test_keymode_legacy(self):
        storage = S3ClusterStorage(bucket=TEST_BUCKET_NAME,
                                   prefix='testlayer',
                                   pyramid=self.pyramid,
                                   key_mode='legacy',
                                   mimetype='image/png')
        storage.put(self.metatile)

        self.assertIsNotNone(self.conn.get_bucket(TEST_BUCKET_NAME).get_key(
            'testlayer/19/01/9E/BB/B3/19-453824-212288@8.zip'))
        storage.close()

    def test_keymode_hilbert(self):
        storage = S3ClusterStorage(bucket=TEST_BUCKET_NAME,
                                   prefix='testlayer',
                                   pyramid=self.pyramid,
                                   key_mode='hilbert',
                                   mimetype='image/png')
        storage.put(self.metatile)

        self.assertIsNotNone(self.conn.get_bucket(TEST_BUCKET_NAME).get_key(
            'testlayer/19/03/35/B0/B6/19-453824-212288@8.zip'))

        storage.close()

    def tearDown(self):
        self.conn.close()
        self.mock.stop()


class TestS3MetaTileStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()
        self.conn = boto.connect_s3()
        self.conn.create_bucket(TEST_BUCKET_NAME)

        self.pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                                 data=open(grid_image, 'rb').read(),
                                 mimetype='image/png')

    def test_basic(self):
        storage = S3MetaTileStorage(
            pyramid=self.pyramid,
            bucket=TEST_BUCKET_NAME,
            prefix='testlayer',
            mimetype='image/png')
        storage.put(self.metatile)

        metatile = storage.get(self.metatile.index)
        self.assertIsInstance(metatile, MetaTile)
        self.assertEqual(metatile.index, self.metatile.index)
        self.assertAlmostEqual(metatile.mtime, self.metatile.mtime, 0)
        self.assertEqual(metatile.etag, self.metatile.etag)
        self.assertEqual(metatile.mimetype, self.metatile.mimetype)

        storage.retire(self.metatile.index)
        self.assertIsNone(storage.get(self.metatile.index))
        storage.close()

    def tearDown(self):
        self.conn.close()
        self.mock.stop()


if __name__ == '__main__':
    unittest.main()
