# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

import unittest

from stonemason.renderer.layerexpr import *


class TestTerminalLayer(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.layer = TerminalLayer(self.name)

    def test_name(self):
        self.assertEqual(self.name, self.layer.name)

    def test_repr(self):
        self.assertEqual("TerminalLayer(name='test')", repr(self.layer))


class TestTransformLayer(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.layer = TransformLayer('test', TerminalLayer('test1'))

    def test_nama(self):
        self.assertEqual(self.name, self.layer.name)

    def test_repr(self):
        self.assertEqual(
            "TransformLayer(name='test', TerminalLayer(name='test1'))",
            repr(self.layer))


class TestCompositeLayer(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.layer = CompositeLayer(
            'test', [TerminalLayer('test1'), TerminalLayer('test2')])

    def test_name(self):
        self.assertEqual(self.name, self.layer.name)

    def test_repr(self):
        self.assertEqual(
            "CompositeLayer(name='test', TerminalLayer(name='test1'), TerminalLayer(name='test2'))",
            repr(self.layer))
