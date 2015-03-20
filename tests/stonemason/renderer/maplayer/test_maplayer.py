# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/20/15'

import unittest

from stonemason.renderer.maplayer import LeafLayer, Transformer, Compositor


class TestBaseLayer(unittest.TestCase):
    def setUp(self):
        self._layer = LeafLayer('base')

    def test_name(self):
        self.assertEqual('base', self._layer.name)

    def test_repr(self):
        self.assertEqual("LeafLayer(name='base')", repr(self._layer))


class TestTransformLayer(unittest.TestCase):
    def setUp(self):
        base = LeafLayer('base')
        self._layer = Transformer('transformer', base)

    def test_name(self):
        self.assertEqual('transformer', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "Transformer(name='transformer', LeafLayer(name='base'))",
            repr(self._layer))


class TestCompositeLayer(unittest.TestCase):
    def setUp(self):
        base1 = LeafLayer('base1')
        base2 = LeafLayer('base2')

        self._layer = Compositor('compositor', base1, base2)

    def test_name(self):
        self.assertEqual('compositor', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "Compositor(name='compositor', LeafLayer(name='base1'), LeafLayer(name='base2'))",
            repr(self._layer))
