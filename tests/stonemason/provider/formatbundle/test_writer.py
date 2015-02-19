# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/19/15'

import unittest
import os
import io

from PIL import Image

from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle, \
    MapWriter

from tests import DATA_DIRECTORY


class TestImageMapWriter(unittest.TestCase):
    def setUp(self):
        bundle = FormatBundle(MapType('image'),
                              TileFormat('JPEG',
                                         parameters=dict(quality=60)))
        self.writer = bundle.writer

        grid_image = os.path.join(DATA_DIRECTORY,
                                  'grid_crop', 'grid.png')
        self.image_data = open(grid_image, mode='rb').read()
        self.image = Image.open(grid_image)

    def test_crop_map(self):
        data = self.writer.crop_map(self.image, buffer=256)
        image = Image.open(io.BytesIO(data))
        self.assertEqual(image.format, 'JPEG')
        self.assertTupleEqual(image.size, (512, 512))

    def test_gridcrop_map(self):
        for (row, column), image_data in self.writer.grid_crop_map(self.image,
                                                                   stride=2,
                                                                   buffer=256):
            grid_image = Image.open(io.BytesIO(image_data))
            self.assertEqual(grid_image.format, 'JPEG')
            self.assertTupleEqual(grid_image.size, (256, 256))

    def test_resplit_map(self):
        for (row, column), image_data in self.writer.resplit_map(
                self.image_data,
                stride=2,
                buffer=256):
            grid_image = Image.open(io.BytesIO(image_data))
            self.assertEqual(grid_image.format, 'JPEG')
            self.assertEqual(grid_image.size, (256, 256))


if __name__ == '__main__':
    unittest.main()
