# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '12/25/14'

import os
import unittest

from PIL import Image

DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), 'data')


class ImageTestCase(unittest.TestCase):
    def assertImageEqual(self, first, second):
        assert isinstance(first, Image.Image)
        assert isinstance(second, Image.Image)
        # NOTE: We can't use TestCase.assertEqual() here since it will try to
        # generate a extremely large "diff report" if test fails.
        self.assertTrue(list(first.getdata()) == list(second.getdata()))

    def assertImageNotEqual(self, first, second):
        assert isinstance(first, Image.Image)
        assert isinstance(second, Image.Image)
        self.assertFalse(list(first.getdata()) == list(second.getdata()))
