# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/20/15'

import os

from PIL import Image

from stonemason.renderer.cartographer import MapnikLayer
from stonemason.renderer.maplayer import MapContext
from stonemason.provider.pyramid import Pyramid

from tests import SAMPLE_THEME_DIRECTORY, DATA_DIRECTORY
from tests import skipUnlessHasMapnik, ImageTestCase


@skipUnlessHasMapnik()
class TestMapnikLayer(ImageTestCase):
    def setUp(self):
        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        style_sheet = os.path.join(theme_root, 'sample_world.xml')

        self._layer = MapnikLayer('mapnik', style_sheet=style_sheet)

    def test_image(self):
        pyramid = Pyramid()

        context = MapContext(
            pyramid=pyramid,
            target_bbox=(-10037508.34, -10037508.34, 10037508.34, 10037508.34),
            target_size=(512, 512),
        )

        image = self._layer.image(context)

        test_data_root = os.path.join(DATA_DIRECTORY, 'cartographer')
        test_file = os.path.join(test_data_root, 'mapnik_sample_world.png')
        # image.save(test_file, 'png')

        expected = Image.open(test_file)
        self.assertImageEqual(expected, image)