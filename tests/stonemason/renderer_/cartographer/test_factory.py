# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import os
import unittest

from stonemason.renderer_.cartographer import LayerFactory
from stonemason.renderer_.cartographer.imagery import \
    Black, Mapnik_, Invert, AlphaBlend, HAS_MAPNIK

from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY

style_sheet = os.path.join(
    SAMPLE_THEME_DIRECTORY, 'sample_world', 'sample_world.xml')


class TestLayerFactory(unittest.TestCase):
    def setUp(self):
        self.factory = LayerFactory()

    def test_create_terminal_layer(self):
        layer = self.factory.create_terminal_layer('test', 'pil.black')
        self.assertIsInstance(layer, Black)

        if HAS_MAPNIK:
            layer = self.factory.create_terminal_layer(
                'test', 'mapnik', style_sheet=style_sheet)
            self.assertIsInstance(layer, Mapnik_)

    def test_create_transform_layer(self):
        source = self.factory.create_terminal_layer('test', 'pil.black')

        layer = self.factory.create_transform_layer(
            'test', 'pil.invert', source=source)
        self.assertIsInstance(layer, Invert)

    def test_create_composite_layer(self):
        source1 = self.factory.create_terminal_layer('test', 'pil.black')
        source2 = self.factory.create_terminal_layer('test', 'pil.black')

        layer = self.factory.create_composite_layer(
            'test', 'pil.blend.alpha', sources=[source1, source2])
        self.assertIsInstance(layer, AlphaBlend)
