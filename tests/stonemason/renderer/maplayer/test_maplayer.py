# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/20/15'

import unittest

from stonemason.renderer.map import BaseLayer, TransformLayer, CompositeLayer


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
        self._layer = TransformLayer('transformer', base)

    def test_name(self):
        self.assertEqual('transformer', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "TransformLayer(name='transformer', BaseLayer(name='base'))",
            repr(self._layer))


class TestCompositeLayer(unittest.TestCase):
    def setUp(self):
        base1 = BaseLayer('base1')
        base2 = BaseLayer('base2')

        self._layer = CompositeLayer('compositor', layers=[base1, base2])

    def test_name(self):
        self.assertEqual('compositor', self._layer.name)

    def test_repr(self):
        self.assertEqual(
            "CompositeLayer(name='compositor', BaseLayer(name='base1'), BaseLayer(name='base2'))",
            repr(self._layer))
