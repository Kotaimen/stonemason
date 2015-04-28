# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from PIL import Image

from stonemason.renderer.cartographer.imagery import Color, Invert, Blend
from stonemason.renderer.context import RenderContext

from tests import ImageTestCase


class TestColor(ImageTestCase):
    def setUp(self):
        self.layer = Color('test', color='Black')

    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (0, 0, 0))

        self.assertImageEqual(expected, feature.data)


class TestInvert(ImageTestCase):
    def setUp(self):
        self.layer = Invert('invert', layer=Color('source', color='Black'))

    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (255, 255, 255))

        self.assertImageEqual(expected, feature.data)


class TestBlend(ImageTestCase):
    def setUp(self):
        source1 = Invert('source1', layer=Color('source', color='Black'))
        source2 = Color('source2', color='Black')

        self.layer = Blend('blend', layers=[source1, source2], alpha=0.5)


    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (127, 127, 127))

        self.assertImageEqual(expected, feature.data)
