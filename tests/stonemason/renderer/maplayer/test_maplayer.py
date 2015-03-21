# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/20/15'

import unittest

from stonemason.renderer.map import BaseLayer, Transformer, Compositor


class TestBaseLayer(unittest.TestCase):
    def setUp(self):
        self._layer = BaseLayer('base')

    def test_name(self):
        self.assertEqual('base', self._layer.name)

    def test_repr(self):
        self.assertEqual("BaseLayer(name='base')", repr(self._layer))


class TestTransformLayer(unittest.TestCase):
    def setUp(self):
        base = BaseLayer('base')
        self._layer = Transformer('transformer', base)

    def test_name(self):
        self.assertEqual('transformer', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "Transformer(name='transformer', BaseLayer(name='base'))",
            repr(self._layer))


class TestCompositeLayer(unittest.TestCase):
    def setUp(self):
        base1 = BaseLayer('base1')
        base2 = BaseLayer('base2')

        self._layer = Compositor('compositor', base1, base2)

    def test_name(self):
        self.assertEqual('compositor', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "Compositor(name='compositor', BaseLayer(name='base1'), BaseLayer(name='base2'))",
            repr(self._layer))
