# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

import unittest

from stonemason.renderer.engine.rendernode import *


class TestTerminalNode(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.node = TermNode(self.name)

    def test_name(self):
        self.assertEqual(self.name, self.node.name)

    def test_repr(self):
        expected = "TermNode('test')"
        self.assertEqual(expected, repr(self.node))


class TestTransformNode(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.node = TransformNode('test', TermNode('test1'))

    def test_name(self):
        self.assertEqual(self.name, self.node.name)

    def test_repr(self):
        expected = "TransformNode('test', TermNode('test1'))"
        self.assertEqual(expected, repr(self.node))


class TestCompositeNode(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.node = CompositeNode(
            'test', [TermNode('test1'), TermNode('test2')])

    def test_name(self):
        self.assertEqual(self.name, self.node.name)

    def test_repr(self):
        expected = "CompositeNode('test', TermNode('test1'), TermNode('test2'))"
        self.assertEqual(expected, repr(self.node))
