# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/10/15'

import unittest
import os

from PIL import Image
from tests import DATA_DIRECTORY, TEST_DIRECTORY

TEST_DIRECTORY = os.path.join(TEST_DIRECTORY, 'pil_test')


class TestPIL(unittest.TestCase):
    """Verify necessary PIL format plugins are corrected built in case of
    misconfiguration.
    """

    def setUp(self):
        if not os.path.exists(TEST_DIRECTORY):
            os.mkdir(TEST_DIRECTORY)
        self.photo = Image.open(
            os.path.join(DATA_DIRECTORY, 'sample-photo.jpg'))
        self.map = Image.open(os.path.join(DATA_DIRECTORY, 'sample-map.png'))
        self.map = self.map.convert('RGB')

    def test_save_png(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-png24.png'),
                        format='PNG', optimize=True)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-png24.png'),
                      format='PNG', optimize=True)
        self.map.convert(mode='P', colors=64).save(
            os.path.join(TEST_DIRECTORY, 'map-png8-64.png'),
            format='PNG', optimize=True)

    def test_save_jpeg(self):
        self.photo.save(
            os.path.join(TEST_DIRECTORY, 'photo-jpeg-quality=90.jpg'),
            format='JPEG', optimize=True, quality=90)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-jpeg-quality=90.jpg'),
                      format='JPEG', optimize=True, quality=90)
        self.photo.save(
            os.path.join(TEST_DIRECTORY, 'photo-jpeg-quality=60.jpg'),
            format='JPEG', optimize=True, quality=60)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-jpeg-quality=60.jpg'),
                      format='JPEG', optimize=True, quality=60)

    def test_save_tiff(self):
        self.photo.save(os.path.join(TEST_DIRECTORY, 'photo-tiff.tif'),
                        format='TIFF')
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-tiff.tif'),
                      format='TIFF')

    def test_save_webp(self):
        self.photo.save(
            os.path.join(TEST_DIRECTORY, 'photo-webp-lossless.webp'),
            format='WEBP', lossless=True)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-webp-lossless.webp'),
                      format='WEBP', lossless=True)
        self.photo.save(
            os.path.join(TEST_DIRECTORY, 'photo-webp-quality=90.webp'),
            format='WEBP', quality=90)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-webp-quality=90.webp'),
                      format='WEBP', quality=90)
        self.photo.save(
            os.path.join(TEST_DIRECTORY, 'photo-webp-quality=60.webp'),
            format='WEBP', quality=60)
        self.map.save(os.path.join(TEST_DIRECTORY, 'map-webp-quality=60.webp'),
                      format='WEBP', quality=60)


if __name__ == '__main__':
    unittest.main()
