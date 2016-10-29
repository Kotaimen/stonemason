# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/18/15'

import os
import tempfile
import unittest
import shutil
import moto
import boto

from PIL import Image

try:
    from stonemason.renderer.cartographer.image.terminal import DiskStorageNode, \
        S3StorageNode
except ImportError as e:
    raise unittest.SkipTest(str(e))

from stonemason.renderer import RenderContext
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.pyramid import Pyramid, MetaTile, MetaTileIndex
from stonemason.storage import DiskMetaTileStorage, S3MetaTileStorage

from tests import DATA_DIRECTORY, ImageTestCase


class TestDiskStorageNode(ImageTestCase):
    def setUp(self):
        root = tempfile.mkdtemp()
        pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop', 'grid.png')

        metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                            data=open(grid_image, 'rb').read(),
                            mimetype='image/png')
        format = FormatBundle(MapType('image'), TileFormat('PNG'))
        storage = DiskMetaTileStorage(levels=pyramid.levels,
                                      stride=pyramid.stride,
                                      root=root,
                                      format=format)
        storage.put(metatile)

        self.root = root
        self.node = DiskStorageNode('disk', maptype='image',
                                    tileformat=dict(format='PNG'),
                                    stride=pyramid.stride,
                                    root=self.root)
        self.expected = grid_image

    def test_render(self):
        context = RenderContext(
            meta_index=MetaTileIndex(19, 453824, 212288, 8))

        image = self.node.render(context).data

        expected = Image.open(self.expected)
        self.assertImageEqual(expected, image)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)


TEST_BUCKET_NAME = 'tilestorage'


class TestS3StorageNode(ImageTestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()
        self.conn = boto.connect_s3()
        self.conn.create_bucket(TEST_BUCKET_NAME)
        pyramid = Pyramid(stride=8)
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop', 'grid.png')

        metatile = MetaTile(MetaTileIndex(19, 453824, 212288, 8),
                            data=open(grid_image, 'rb').read(),
                            mimetype='image/png')
        format = FormatBundle(MapType('image'), TileFormat('PNG'))

        storage = S3MetaTileStorage(levels=pyramid.levels,
                                    stride=pyramid.stride,
                                    bucket=TEST_BUCKET_NAME,
                                    prefix='testlayer',
                                    format=format)
        storage.put(metatile)

        self.node = S3StorageNode('s3', maptype='image',
                                  tileformat=dict(format='PNG'),
                                  levels=pyramid.levels,
                                  stride=pyramid.stride,
                                  bucket=TEST_BUCKET_NAME,
                                  prefix='testlayer')
        self.expected = grid_image

    def test_render(self):
        context = RenderContext(
            meta_index=MetaTileIndex(19, 453824, 212288, 8))

        image = self.node.render(context).data

        expected = Image.open(self.expected)
        self.assertImageEqual(expected, image)

    def tearDown(self):
        self.conn.close()
        self.mock.stop()
