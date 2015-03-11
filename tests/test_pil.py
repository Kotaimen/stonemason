# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/10/15'

import unittest
import os

from PIL import Image
from tests import DATA_DIRECTORY, TEST_DIRECTORY


class TestPIL(unittest.TestCase):
    """Verify necessary PIL format plugins are corrected built in case of
    misconfiguration.
    """

    def setUp(self):
        self.photo = Image.open(
            os.path.join(DATA_DIRECTORY, 'sample-photo.jpg'))
        self.map = Image.open(os.path.join(DATA_DIRECTORY, 'sample-map.png'))


    def test_save_png(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo.png'),
                        format='PNG', optimize=True)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map.png'),
                      format='PNG', optimize=True)


    def test_save_jpeg(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-quality=90.jpg'),
                        format='JPEG', optimize=True, quality=90)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-quality=90.jpg'),
                      format='JPEG', optimize=True, quality=90)
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-quality=80.jpg'),
                        format='JPEG', optimize=True, quality=80)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-quality=80.jpg'),
                      format='JPEG', optimize=True, quality=80)

    def test_save_tiff(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo.tif'),
                        format='TIFF')
        self.map.save(os.path.join(TEST_DIRECTORY, 'map.tif'),
                      format='TIFF')

    def test_save_webp(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-lossless.webp'),
                        format='WEBP', lossless=True)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-lossless.webp'),
                      format='WEBP', lossless=True)
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-quality=90.webp'),
                        format='WEBP', quality=90)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-quality=90.webp'),
                      format='WEBP', quality=90)
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-quality=80.webp'),
                        format='WEBP', quality=80)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-quality=80.webp'),
                      format='WEBP', quality=80)


if __name__ == '__main__':
    unittest.main()
