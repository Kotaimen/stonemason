# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

import unittest
import os
from distutils.version import StrictVersion

import PIL
from PIL import Image
from six import print_

from stonemason.util.postprocessing.gridcrop import *
from tests import DATA_DIRECTORY


class TestPIL(unittest.TestCase):
    def setUp(self):
        grid_image = os.path.join(DATA_DIRECTORY, 'grid_crop',
                                  'paletted_grid.png')
        self.grid_data = open(grid_image, mode='rb').read()
        self.grid_file = open(grid_image, mode='rb')
        self.grid_image = Image.open(grid_image)

    def test_version(self):
        try:
            # Any reasonably recent Pillow is fine
            self.assertGreaterEqual(StrictVersion(PIL.PILLOW_VERSION),
                                    StrictVersion('2.0.0'))
        except AttributeError:
            # PIL must be 1.1.7
            self.assertEqual(StrictVersion(PIL.VERSION),
                             StrictVersion('1.1.7'))

    def test_grid_crop(self):

        self.assertEqual(
            len(grid_crop(self.grid_data, stride=2, buffer_size=0)),
            4)
        self.assertEqual(
            len(grid_crop(self.grid_data, stride=4, buffer_size=0)),
            16)
        self.assertEqual(
            len(grid_crop(self.grid_data, stride=1, buffer_size=0)),
            1)
        self.assertEqual(
            len(grid_crop(self.grid_data, stride=2, buffer_size=256)),
            4)


if __name__ == '__main__':
    unittest.main()
