# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from PIL import Image

from stonemason.renderer_ import MasonRenderer, RenderContext
from tests import ImageTestCase


class TestMasonRenderer(ImageTestCase):
    def setUp(self):
        expr = {
            'root': {
                'prototype': 'pil.blend.alpha',
                'sources': ['l1', 'l2'],

            },
            'l1': {
                'prototype': 'pil.invert',
                'source': 'l3'
            },
            'l2': {
                'prototype': 'pil.black',
            },
            'l3': {
                'prototype': 'pil.black',
            }
        }

        self.renderer = MasonRenderer(expr)

    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.renderer.render(context)

        expected = Image.new('RGB', (256, 256), (127, 127, 127))

        self.assertImageEqual(expected, feature.data)

