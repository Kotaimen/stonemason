# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/24/15'

import unittest
import os
import io
import zipfile
import json

from PIL import Image

from stonemason.provider.pyramid import MetaTile, MetaTileIndex, \
    TileIndex, Tile, Pyramid
from stonemason.provider.tilestorage import Splitter, ImageSplitter, \
    TileCluster
from stonemason.provider.tilestorage.cluster import guess_extension, \
    guess_mimetype

from tests import DATA_DIRECTORY, ImageTestCase


class TestImageSplitter(ImageTestCase):
    def setUp(self):
        self.splitter = ImageSplitter(format='JPEG')
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.image_data = open(grid_image, mode='rb').read()
        self.image = Image.open(grid_image)

    def test_split(self):
        for (row, column), image_data in self.splitter(self.image,
                                                       stride=2,
                                                       buffer=256):
            grid_image = Image.open(io.BytesIO(image_data))
            self.assertEqual(grid_image.format, 'JPEG')
            self.assertEqual(grid_image.size, (256, 256))


class TestCreateTileClusterFromMetaTile(ImageTestCase):
    def setUp(self):
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.image_data = open(grid_image, mode='rb').read()
        self.image = Image.open(grid_image)

        self.metatile = MetaTile(MetaTileIndex(4, 4, 8, 2),
                                 data=self.image_data,
                                 mimetype='image/png',
                                 buffer=256)
        self.splitter = ImageSplitter()

    def test_from_metatile(self):
        tilecluster = TileCluster.from_metatile(self.metatile)
        self.assertIsInstance(tilecluster, TileCluster)
        self.assertEqual(tilecluster.index, self.metatile.index)
        self.assertEqual(len(tilecluster.tiles), 4)
        self.assertSetEqual(
            {TileIndex(4, 4, 8), TileIndex(4, 5, 8),
             TileIndex(4, 4, 9), TileIndex(4, 5, 9)},
            {tile.index for tile in tilecluster.tiles}
        )
        ref_image = self.image.crop(
            (256, 512, 512, 768))
        for tile in tilecluster.tiles:
            if tile.index == TileIndex(4, 4, 9):
                self.assertImageEqual(Image.open(io.BytesIO(tile.data)),
                                      ref_image)


class TestCreateTileClusterFromZipFile(ImageTestCase):
    def setUp(self):
        self.zip_file = os.path.join(DATA_DIRECTORY,
                                     'storage',
                                     'test-cluster.zip')

    def test_from_zip(self):
        with open(self.zip_file, 'rb') as fp:
            tilecluster = TileCluster.from_zip(fp)
            self.assertIsInstance(tilecluster, TileCluster)
            self.assertEqual(tilecluster.index, MetaTileIndex(4, 4, 8, 2))
            for tile in tilecluster.tiles:
                if tile.index == TileIndex(4, 4, 8):
                    self.assertEqual(tile.data, b'4-4-8')
                    self.assertEqual(tile.mtime, 1422151500.0)
                    self.assertEqual(tile.mimetype, 'text/plain')
                if tile.index == TileIndex(4, 4, 9):
                    self.assertEqual(tile.data, b'4-4-9')
                    self.assertEqual(tile.mtime, 1422151500.0)
                    self.assertEqual(tile.mimetype, 'text/plain')
                if tile.index == TileIndex(4, 5, 8):
                    self.assertEqual(tile.data, b'4-4-9')
                    self.assertEqual(tile.mtime, 1422151500.0)
                    self.assertEqual(tile.mimetype, 'text/plain')
                if tile.index == TileIndex(4, 5, 9):
                    self.assertEqual(tile.data, b'4-5-9')
                    self.assertEqual(tile.mtime, 1422151500.0)
                    self.assertEqual(tile.mimetype, 'text/plain')

    def test_from_zip_with_metadata(self):
        with open(self.zip_file, 'rb') as fp:
            metadata = dict(mtime=0.0, mimetype='text/tile', stride=None)
            tilecluster = TileCluster.from_zip(fp, metadata)
            self.assertIsInstance(tilecluster, TileCluster)
            self.assertEqual(tilecluster.index, MetaTileIndex(4, 4, 8, 2))
            for tile in tilecluster.tiles:
                if tile.index == TileIndex(4, 5, 8):
                    self.assertEqual(tile.data, b'4-4-9')
                    self.assertEqual(tile.mtime, 0.0)
                    self.assertEqual(tile.mimetype, 'text/tile')
                    break


class TestCreateTileClusterFromLegacyZipFile(ImageTestCase):
    def test_from_zip_1(self):
        zip_file = os.path.join(DATA_DIRECTORY,
                                'storage',
                                '4-0-0@8.zip')

        with open(zip_file, 'rb') as fp:
            tilecluster = TileCluster.from_zip(fp)
            self.assertIsInstance(tilecluster, TileCluster)
            self.assertEqual(tilecluster.index, MetaTileIndex(4, 0, 0, 8))

    def test_from_zip_2(self):
        zip_file = os.path.join(DATA_DIRECTORY,
                                'storage',
                                '19-468416-187664@8.zip')

        with open(zip_file, 'rb') as fp:
            tilecluster = TileCluster.from_zip(fp)
            self.assertIsInstance(tilecluster, TileCluster)
            self.assertEqual(tilecluster.index,
                             MetaTileIndex(19, 468416, 187664, 8))


class TxtSplitter(Splitter):
    def __call__(self, data, stride, buffer):
        for x in range(stride):
            for y in range(stride):
                yield (x, y), b'tile_data'


class TestSaveClusterAsZipFile(unittest.TestCase):
    def setUp(self):
        metatile = MetaTile(MetaTileIndex(3, 0, 0, 2),
                            data=b'metatile_data',
                            mimetype='text/plain',
                            mtime=1.,
                            buffer=0)

        self.cluster = TileCluster.from_metatile(metatile,
                                                 splitter=TxtSplitter())

        self.expected_index = {
            "version": 1,
            "mimetype": "text/plain",
            "tiles": {
                "3-1-1": "3-0-0",
                "3-1-0": "3-0-0",
                "3-0-0": "3-0-0",
                "3-0-1": "3-0-0"
            },
            "extension": ".txt",
            "stride": 2,
            "mtime": 1.0,
            "datas": [
                "3-0-0"
            ]
        }
        self.expected_data = b'tile_data'

    def test_save_as_zip(self):
        buffer = io.BytesIO()
        self.cluster.save_as_zip(buffer)
        zip_file = zipfile.ZipFile(buffer)
        index = json.loads(zip_file.read('index.json').decode('utf-8'))
        self.assertDictEqual(index,
                             self.expected_index)
        for tile in self.cluster.tiles:
            self.assertEqual(tile.data, self.expected_data)
            self.assertEqual(tile.mimetype, 'text/plain')
            self.assertEqual(tile.mtime, 1.0)

    def test_save_as_zip_compressed(self):
        buffer1 = io.BytesIO()
        buffer2 = io.BytesIO()
        self.cluster.save_as_zip(buffer1)
        self.cluster.save_as_zip(buffer2, compressed=True)
        self.assertGreater(len(buffer1.getvalue()),
                           len(buffer2.getvalue()))


if __name__ == '__main__':
    unittest.main()
