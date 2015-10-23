# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/9/15'

import os
import shutil
import tempfile
import unittest

from stonemason.pyramid import MetaTile, MetaTileIndex, Pyramid, TileCluster
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.storage.tile import Clusterfier, DiskMetaTileStorage
from tests import DATA_DIRECTORY


class TestClusterfier(unittest.TestCase):
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

        cluster_storage = Clusterfier(storage, self.format.writer)
        cluster_storage.put(self.metatile)

        metatile = storage.get(self.metatile.index)
        self.assertIsInstance(metatile, MetaTile)

        cluster = cluster_storage.get(self.metatile.index)
        self.assertIsInstance(cluster, TileCluster)
        self.assertTrue(storage.has(self.metatile.index))
        self.assertEqual(metatile.index, cluster.index)

        cluster_storage.retire(self.metatile.index)
        self.assertIsNone(cluster_storage.get(self.metatile.index))
        self.assertFalse(storage.has(self.metatile.index))

        self.assertListEqual(self.pyramid.levels, storage.levels)
        self.assertEqual(self.pyramid.stride, storage.stride)

        cluster_storage.close()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
