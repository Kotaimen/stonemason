# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '12/25/14'

import os
import unittest
import subprocess
import importlib

from unittest.case import skipUnless

#
# Data directory
#

# For test data
DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), 'data')

# For temporary test output, visual confirm
TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'output')

if not os.path.exists(TEST_DIRECTORY):
    os.mkdir(TEST_DIRECTORY)

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

carto = importlib.import_module('stonemason.renderer.cartographer.imagery')


def skipUnlessHasMapnik():
    return skipUnless(carto.HAS_MAPNIK, 'python-mapnik not installed.')


def skipUnlessHasImageMagick():
    return skipUnless(carto.HAS_IMAGEMAGICK, 'imagemagick not installed.')


def skipUnlessHasScipy():
    return skipUnless(carto.HAS_SCIPY, 'scipy not installed.')

def skipUnlessHasSkimage():
    return skipUnless(carto.HAS_SKIMAGE, 'scikit-skimage not installed.')


geo = importlib.import_module('stonemason.pyramid.geo')


def skipUnlessHasGDAL():
    return skipUnless(geo.HAS_GDAL, 'python-gdal not installed.')


import pylibmc

c = pylibmc.Client(servers=['127.0.0.1:11211'])
try:
    c.get_stats()
except pylibmc.Error:
    HAS_LOCAL_MEMCACHE = False
else:
    HAS_LOCAL_MEMCACHE = True
finally:
    del c


def skipUnlessHasLocalMemcacheServer():
    return skipUnless(HAS_LOCAL_MEMCACHE, 'memcache not installed.')
