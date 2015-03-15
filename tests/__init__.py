# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '12/25/14'

import os
import unittest
import importlib

from unittest.case import skipUnless

#
# Data directory
#

# For test data
DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), 'data')

# For temporary test output, visual confirm
TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'output')

SAMPLE_THEME_DIRECTORY = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.pardir,
    'stonemason', 'mason', 'theme', 'samples',
))

#
# Image test base
#
from PIL import Image, ImageChops, ImageStat


class ImageTestCase(unittest.TestCase):
    """Comparing images pixel by pixel."""

    def assertImageEqual(self, first, second):
        assert isinstance(first, Image.Image)
        assert isinstance(second, Image.Image)

        diff = ImageChops.difference(first, second)
        stat = ImageStat.Stat(diff)

        self.assertAlmostEqual(sum(stat.sum), 0.0)

    def assertImageNotEqual(self, first, second):
        assert isinstance(first, Image.Image)
        assert isinstance(second, Image.Image)

        diff = ImageChops.difference(first, second)
        stat = ImageStat.Stat(diff)

        self.assertGreater(sum(stat.sum), 0.0)

#
# Conditional tests for optional decencies
#
try:
    importlib.import_module('mapnik')

    HAS_MAPNIK = True
except ImportError:
    HAS_MAPNIK = False


def skipUnlessHasMapnik():
    return skipUnless(HAS_MAPNIK, 'python-mapnik not installed.')


try:
    importlib.import_module('osgeo.osr')
    importlib.import_module('osgeo.ogr')
    importlib.import_module('osgeo.gdal')
    HAS_GDAL = True
except ImportError:
    HAS_GDAL = False


def skipUnlessHasGDAL():
    return skipUnless(HAS_GDAL, 'python-gdal not installed.')


try:
    importlib.import_module('stonemason.util.postprocessing.magickcmd')

    HAS_IMAGEMAGICK = True
except ImportError:
    raise
    HAS_IMAGEMAGICK = False


def skipUnlessHasImageMagick():
    return skipUnless(HAS_IMAGEMAGICK, 'Imagemagick not installed.')
