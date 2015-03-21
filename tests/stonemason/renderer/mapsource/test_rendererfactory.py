# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/21/15'

import os
import unittest

from tests import SAMPLE_THEME_DIRECTORY
from tests import skipUnlessHasImageMagick, HAS_MAPNIK

from stonemason.renderer.cartographer import MapnikRenderer
from stonemason.renderer.mapsource import ImageMapRendererFactory


class TestImageRendererFactory(unittest.TestCase):
    def test_create_invalid_renderer(self):
        self.assertRaises(
            ValueError,
            ImageMapRendererFactory().create_renderer, 'dummy', 'bob')

    def test_create_mapnik_renderer(self):
        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        style_sheet = os.path.join(theme_root, 'sample_world.xml')

        if HAS_MAPNIK:
            renderer = ImageMapRendererFactory().create_renderer(
                'mapnik', 'roads', style_sheet=style_sheet)
            self.assertIsInstance(renderer, MapnikRenderer)
        else:
            self.assertRaises(
                ValueError,
                ImageMapRendererFactory().create_renderer,
                'mapnik', 'roads', style_sheet=style_sheet)
