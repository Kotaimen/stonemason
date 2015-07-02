# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import os

from stonemason.renderer.cartographer.imagery.pilcarto import *
from stonemason.renderer.context import RenderContext

from tests import ImageTestCase
from tests import DATA_DIRECTORY

BLENDING_DIRECTORY = os.path.join(DATA_DIRECTORY, 'blending')


class TestColor(ImageTestCase):
    def setUp(self):
        self.layer = PILColor('test', color='Black')

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
        self.layer = PILInvert('invert',
                               layer=PILColor('source', color='Black'))

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
        source1 = PILInvert('source1', layer=PILColor('source', color='Black'))
        source2 = PILColor('source2', color='Black')

        self.layer = PILBlend('blend', layers=[source1, source2], alpha=0.5)

    def test_render(self):
        context = RenderContext(
            map_proj='EPSG:3857',
            map_bbox=(-180, -85, 180, 85),
            map_size=(256, 256),
            scale_factor=1)

        feature = self.layer.render(context)

        expected = Image.new('RGB', (256, 256), (127, 127, 127))

        self.assertImageEqual(expected, feature.data)


class TestPILCompose(ImageTestCase):
    def test_overlay(self):
        dst_filename = os.path.join(
            BLENDING_DIRECTORY, 'gradient_grey.png')
        src_filename = os.path.join(
            BLENDING_DIRECTORY, 'gradient_yell-blue.png')

        tgt_filename = os.path.join(
            BLENDING_DIRECTORY, 'overlay.png'
        )

        dst = Image.open(dst_filename)
        src = Image.open(src_filename)

        result = pil_overlay(dst, src)

        expected = Image.open(tgt_filename)
        expected = expected.convert('RGBA')

        self.assertEqual(expected.mode, result.mode)
        self.assertEqual(expected.format, result.format)
        self.assertImageEqual(expected, result)

