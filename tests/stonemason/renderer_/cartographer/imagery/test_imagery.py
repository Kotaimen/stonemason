# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from PIL import Image

from stonemason.renderer.cartographer.imagery import Black, Invert, AlphaBlend
from stonemason.renderer.context import RenderContext

from tests import ImageTestCase


class TestBlack(ImageTestCase):
    def setUp(self):
        self.layer = Black('test')

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
        self.layer = Invert('invert', layer=Black('source'))

    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (255, 255, 255))

        self.assertImageEqual(expected, feature.data)


class TestAlphaBlend(ImageTestCase):
    def setUp(self):
        source1 = Invert('source1', layer=Black('source'))
        source2 = Black('source2')

        self.layer = AlphaBlend('blend', layers=[source1, source2], alpha=0.5)


    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (127, 127, 127))

        self.assertImageEqual(expected, feature.data)
