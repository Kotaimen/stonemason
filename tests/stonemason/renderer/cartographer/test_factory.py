# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import os
import unittest

from stonemason.renderer.cartographer import LayerFactory
from stonemason.renderer.cartographer.imagery import Color, Filter, Blend

from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY
from tests import skipUnlessHasScipy, skipUnlessHasSkimage

style_sheet = os.path.join(
    SAMPLE_THEME_DIRECTORY, 'sample_world', 'sample_world.xml')


class TestLayerFactory(unittest.TestCase):
    def setUp(self):
        self.factory = LayerFactory()

    def test_create_terminal_layer(self):
        layer = self.factory.create_terminal_layer(
            'test', 'basic.color', color='#000')
        self.assertIsInstance(layer, Color)

    def test_create_transform_layer(self):
        source = self.factory.create_terminal_layer(
            'test', 'basic.color', color='#000')

        layer = self.factory.create_transform_layer(
            'test', 'basic.filter', source=source, filter_name='blur')
        self.assertIsInstance(layer, Filter)

    def test_create_composite_layer(self):
        source1 = self.factory.create_terminal_layer(
            'test', 'basic.color', color='#000')
        source2 = self.factory.create_terminal_layer(
            'test', 'basic.color', color='#000')

        layer = self.factory.create_composite_layer(
            'test', 'basic.blend', sources=[source1, source2], alpha=0.5)
        self.assertIsInstance(layer, Blend)
