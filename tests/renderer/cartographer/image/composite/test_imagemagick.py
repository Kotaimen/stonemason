# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/16/15'

import unittest
import subprocess
import re
import os
from distutils.version import LooseVersion

from PIL import Image

try:
    from stonemason.renderer.cartographer.image.composite.imblender import \
        ImageMagickComposer, ImageMagickError
except ImportError as e:
    raise unittest.SkipTest(str(e))

from tests import DATA_DIRECTORY


class TestImageMagickComposer(unittest.TestCase):
    def setUp(self):
        self.image1 = Image.open(
            os.path.join(DATA_DIRECTORY, 'sample-photo.jpg'))
        self.image2 = Image.open(os.path.join(DATA_DIRECTORY, 'sample-map.png'))

    def test_imagemagick_version(self):
        output = subprocess.check_output(['convert', '-version'])

        match = re.search(r'ImageMagick (\d\.\d+\.\d+)-\d+',
                          output.decode('ascii'))

        if match:
            self.assertGreaterEqual(LooseVersion(match.group(1)),
                                    LooseVersion('6.6.9'))
        else:
            self.assertTrue(False, 'Unable to determinate imagemagick version.')

    def test_compose(self):
        command = '''
        <<image1>> -blur 16
        (
            <<image1>>
            <<image2>> -compose Overlay -composite
        ) -compose Darken -composite
        '''
        co = ImageMagickComposer(command)
        images = dict(image1=self.image1,
                      image2=self.image2)
        result = co.compose(images)
        self.assertIsInstance(result, Image.Image)

    def test_compose_fail(self):
        co = ImageMagickComposer(command='rose: -bad-options -quality 40',
                                 import_format='jpg')
        self.assertRaises(ImageMagickError, co.compose, {})


if __name__ == '__main__':
    unittest.main()
