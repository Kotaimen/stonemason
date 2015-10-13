# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import unittest

from stonemason.renderer.cartographer.image import ImageNodeFactory
from stonemason.renderer.cartographer.image.terminal import Color
from stonemason.renderer.cartographer.image.transform import MinFilter
from stonemason.renderer.cartographer.image.composite import AlphaBlender


class TestImageNodeFactory(unittest.TestCase):
    def setUp(self):
        self.factory = ImageNodeFactory()

    def test_create_terminal_node(self):
        node = self.factory.create_terminal_node(
            'test', 'image.input.color', color='#000')
        self.assertIsInstance(node, Color)

    def test_create_transform_node(self):
        source = self.factory.create_terminal_node(
            'test', 'image.input.color', color='#000')

        node = self.factory.create_transform_node(
            'test', 'image.transform.filter.min', source=source)
        self.assertIsInstance(node, MinFilter)

    def test_create_composite_layer(self):
        source1 = self.factory.create_terminal_node(
            'test', 'image.input.color', color='#000')
        source2 = self.factory.create_terminal_node(
            'test', 'image.input.color', color='#000')

        layer = self.factory.create_composite_node(
            'test', 'image.composite.alphablender', sources=[source1, source2],
            alpha=0.5)
        self.assertIsInstance(layer, AlphaBlender)
