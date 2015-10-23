# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/24/15'

import unittest
import os
import io
import zipfile
import json
import time

from PIL import Image

from stonemason.pyramid import MetaTile, MetaTileIndex, TileIndex, TileCluster
from stonemason.formatbundle import MapType, TileFormat, MapWriter, find_writer
from tests import DATA_DIRECTORY, ImageTestCase


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
        self.writer = find_writer(MapType('image'), TileFormat(format='PNG'))

    def test_from_metatile(self):
        tilecluster = TileCluster.from_metatile(self.metatile, self.writer)
        self.assertIsInstance(tilecluster, TileCluster)
        self.assertEqual(tilecluster.index, self.metatile.index)
        self.assertEqual(len(tilecluster.tiles), 4)
        self.assertSetEqual(
            {TileIndex(4, 4, 8), TileIndex(4, 5, 8),
             TileIndex(4, 4, 9), TileIndex(4, 5, 9)},
            {tile.index for tile in tilecluster.tiles}
        )
        ref_image = self.image.crop((256, 512, 512, 768))
        tile = tilecluster[TileIndex(4, 4, 9)]
        self.assertImageEqual(Image.open(io.BytesIO(tile.data)), ref_image)


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
            tile = tilecluster[TileIndex(4, 4, 8)]
            self.assertEqual(tile.data, b'4-4-8')
            self.assertEqual(tile.mtime, 1422151500.0)
            self.assertEqual(tile.mimetype, 'text/plain')
            tile = tilecluster[TileIndex(4, 4, 9)]
            self.assertEqual(tile.data, b'4-4-9')
            self.assertEqual(tile.mtime, 1422151500.0)
            self.assertEqual(tile.mimetype, 'text/plain')
            tile = tilecluster[TileIndex(4, 5, 8)]
            self.assertEqual(tile.data, b'4-4-9')
            self.assertEqual(tile.mtime, 1422151500.0)
            self.assertEqual(tile.mimetype, 'text/plain')
            tile = tilecluster[TileIndex(4, 5, 9)]
            self.assertEqual(tile.data, b'4-5-9')
            self.assertEqual(tile.mtime, 1422151500.0)
            self.assertEqual(tile.mimetype, 'text/plain')

    def test_from_zip_with_metadata(self):
        with open(self.zip_file, 'rb') as fp:
            metadata = dict(mtime=0.0, mimetype='text/plain', stride=None)
            tilecluster = TileCluster.from_zip(fp, metadata)
            self.assertIsInstance(tilecluster, TileCluster)
            self.assertEqual(tilecluster.index, MetaTileIndex(4, 4, 8, 2))
            tile = tilecluster[TileIndex(4, 5, 8)]
            self.assertEqual(tile.data, b'4-4-9')
            self.assertEqual(tile.mtime, 0.0)
            self.assertEqual(tile.mimetype, 'text/plain')


class TestCreateTileClusterFromFeature(ImageTestCase):
    def setUp(self):
        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.image = Image.open(grid_image)
        self.index = MetaTileIndex(4, 4, 8, 2)
        self.metadata = dict(mimetype='image/png', mtime=time.time())
        self.buffer = 256
        self.writer = find_writer(MapType('image'), TileFormat(format='PNG'))

    def test_from_metatile(self):
        tilecluster = TileCluster.from_feature(self.index,
                                               self.image,
                                               self.metadata,
                                               self.writer,
                                               self.buffer)
        self.assertIsInstance(tilecluster, TileCluster)
        self.assertEqual(tilecluster.index, self.index)
        self.assertEqual(len(tilecluster.tiles), 4)
        self.assertSetEqual(
            {TileIndex(4, 4, 8), TileIndex(4, 5, 8),
             TileIndex(4, 4, 9), TileIndex(4, 5, 9)},
            {tile.index for tile in tilecluster.tiles}
        )
        ref_image = self.image.crop((256, 512, 512, 768))
        tile = tilecluster[TileIndex(4, 4, 9)]
        self.assertImageEqual(Image.open(io.BytesIO(tile.data)), ref_image)


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


class TextMapWriter(MapWriter):
    def __init__(self):
        format_ = TileFormat(format='TXT', mimetype='text/plain')
        super(TextMapWriter, self).__init__(format_)

    def crop_map(self, map, buffer=0):
        raise NotImplementedError

    def grid_crop_map(self, map, stride=1, buffer=0):
        raise NotImplementedError

    def resplit_map(self, data, stride=1, buffer=0):
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
                                                 writer=TextMapWriter())

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
