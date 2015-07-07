# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from PIL import Image

from stonemason.renderer import MasonRenderer, RenderContext
from tests import ImageTestCase


class TestMasonRenderer(ImageTestCase):
    def setUp(self):
        expr = {
            'root': {
                'prototype': 'basic.color',
                'color': '#00f'
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

        expected = Image.new('RGBA', (256, 256), '#00f')

        self.assertImageEqual(expected, feature.data)
