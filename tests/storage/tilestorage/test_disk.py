# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/27/15'

import os
import unittest
import shutil
import tempfile

from stonemason.pyramid import MetaTile, MetaTileIndex, Pyramid, TileCluster
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.storage.tilestorage import DiskClusterStorage, DiskMetaTileStorage, \
    InvalidMetaTile, InvalidMetaTileIndex, ReadOnlyStorage
from tests import DATA_DIRECTORY


class TestDiskClusterStorage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                                 data=open(grid_image, 'rb').read(),
                                 mimetype='image/png')

        self.format = FormatBundle(MapType('image'), TileFormat('PNG'))

    def test_basic(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format)
        storage.put(self.metatile)

        cluster = storage.get(self.metatile.index)
        self.assertIsInstance(cluster, TileCluster)
        self.assertTrue(storage.has(self.metatile.index))

        storage.retire(self.metatile.index)
        self.assertIsNone(storage.get(self.metatile.index))
        self.assertFalse(storage.has(self.metatile.index))
        storage.retire(self.metatile.index)

        self.assertListEqual(self.pyramid.levels, storage.levels)
        self.assertEqual(self.pyramid.stride, storage.stride)

    def test_putfail(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=FormatBundle(MapType('image'), TileFormat('JPEG')))

        self.assertRaises(InvalidMetaTile,
                          storage.put,
                          MetaTile(MetaTileIndex(3, 4, 5, 2)))
        self.assertRaises(InvalidMetaTileIndex,
                          storage.put,
                          MetaTile(MetaTileIndex(100, 4, 5, 2)))
        self.assertRaises(InvalidMetaTile,
                          storage.put,
                          self.metatile)

    def test_readonly(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format,
            readonly=True)
        self.assertRaises(ReadOnlyStorage, storage.put, self.metatile)
        self.assertRaises(ReadOnlyStorage, storage.retire, self.metatile.index)

    def test_pathmode_simple(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format,
            dir_mode='simple')
        storage.put(self.metatile)
        self.assertTrue(os.path.exists(os.path.join(self.root,
                                                    '19',
                                                    '453824',
                                                    '212288',
                                                    '19-453824-212288@8.zip')))

    def test_pathmode_legacy(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format,
            dir_mode='legacy')
        storage.put(self.metatile)
        self.assertTrue(os.path.exists(os.path.join(self.root,
                                                    '19', '01', '9E', 'BB',
                                                    'B3',
                                                    '19-453824-212288@8.zip')))

    def test_pathmode_hilbert(self):
        storage = DiskClusterStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format,
            dir_mode='hilbert')
        storage.put(self.metatile)
        self.assertTrue(os.path.exists(os.path.join(self.root,
                                                    '19', '03', '35', 'B0',
                                                    'B6',
                                                    '19-453824-212288@8.zip')))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)


class TestDiskMetaTileStorage(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                                 data=open(grid_image, 'rb').read(),
                                 mimetype='image/png')
        self.format = FormatBundle(MapType('image'), TileFormat('PNG'))

    def test_basic(self):
        storage = DiskMetaTileStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format)
        storage.put(self.metatile)

        metatile = storage.get(self.metatile.index)
        self.assertIsInstance(metatile, MetaTile)
        self.assertEqual(metatile.index, self.metatile.index)
        self.assertAlmostEqual(metatile.mtime, self.metatile.mtime, delta=1)
        self.assertEqual(metatile.etag, self.metatile.etag)
        self.assertEqual(metatile.mimetype, self.metatile.mimetype)

        self.assertTrue(storage.has(self.metatile.index))
        storage.retire(self.metatile.index)
        self.assertIsNone(storage.get(self.metatile.index))
        self.assertFalse(storage.has(self.metatile.index))

        self.assertListEqual(self.pyramid.levels, storage.levels)
        self.assertEqual(self.pyramid.stride, storage.stride)

    def test_gzip(self):
        storage = DiskMetaTileStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=self.format,
            dir_mode='simple',
            gzip=True)
        storage.put(self.metatile)
        self.assertTrue(os.path.exists(os.path.join(self.root,
                                                    '19', '453824', '212288',
                                                    '19-453824-212288@8.png.gz')))
        metatile = storage.get(self.metatile.index)
        self.assertIsInstance(metatile, MetaTile)

    def test_extension(self):
        storage = DiskMetaTileStorage(
            levels=self.pyramid.levels,
            stride=self.pyramid.stride,
            root=self.root,
            format=FormatBundle(MapType('image'),
                                TileFormat('PNG', extension='.dat')),
            dir_mode='simple', )
        storage.put(self.metatile)
        self.assertTrue(os.path.exists(os.path.join(self.root,
                                                    '19', '453824', '212288',
                                                    '19-453824-212288@8.dat')))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
