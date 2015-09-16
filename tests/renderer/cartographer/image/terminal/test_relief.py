# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/28/15'

import os
import unittest

from PIL import Image

try:
    import numpy as np
    import skimage.filters
    import skimage.external.tifffile
    import skimage.draw
    import skimage.io
    import skimage.morphology
    import skimage.exposure
except ImportError as e:
    raise unittest.SkipTest('Missing Test Dependencies. %s' % str(e))

try:
    from stonemason.renderer.cartographer.image.terminal.relief import \
        simple_shaded_relief, swiss_shaded_relief, array2pillow
except ImportError as e:
    raise unittest.SkipTest(str(e))

from tests import TEST_DIRECTORY


def array2image(array):
    array = array.astype(np.float)
    image = Image.fromarray(array)
    # image = image.convert('RGBA')
    return image


def array2png(array):
    array = array.astype(np.uint8)
    image = Image.fromarray(array, mode='L')
    image = image.convert('RGBA')
    return image


def cone(size=512, z_factor=1.0, padding=16):
    center = (size / 2 - 1, size / 2 - 1)

    def f(x, y):
        z = (size - padding * 2) / 2. - \
            np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        z[z < 0] = 0
        z = z * 2. / size
        z = np.abs(0.2 - z) * 2
        return z

    elevation = np.fromfunction(f, (size, size), dtype=np.float)
    elevation = skimage.filters.gaussian_filter(elevation, sigma=3)
    elevation = skimage.exposure.rescale_intensity(elevation)

    elevation *= z_factor

    return elevation


class TestShadedRelief(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(TEST_DIRECTORY, 'shaded_relief')
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        self.size = 1024
        self.height = 3000.
        self.resolution = self.height / (self.size * 2.)
        self.dem = cone(self.size, z_factor=self.height)

        skimage.io.imsave(os.path.join(self.output_dir, 'elevation.png'),
                          skimage.exposure.rescale_intensity(self.dem))

    def test_simple_shaded_relief(self):
        relief = simple_shaded_relief(self.dem,
                                      (self.resolution,
                                       self.resolution),
                                      scale=1, z_factor=1,
                                      azimuth=315,
                                      altitude=45,
                                      cutoff=0.7071,
                                      gain=5,
                                      )
        image = array2pillow(relief, self.size, self.size)
        filename = os.path.join(self.output_dir, 'simple_cone.png')
        image.save(filename, 'PNG')

    def test_swiss_shaded_relief(self):
        relief = swiss_shaded_relief(self.dem,
                                     (self.resolution,
                                      self.resolution),
                                     scale=1, z_factor=1,
                                     azimuth=315,
                                     )
        image = array2pillow(relief, self.size, self.size)
        filename = os.path.join(self.output_dir, 'swiss_cone.png')
        image.save(filename, 'PNG')
