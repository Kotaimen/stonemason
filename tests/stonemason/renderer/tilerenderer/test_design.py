# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/26/15'

import unittest

from stonemason.renderer.tilerenderer.design import BaseRendererExpr, \
    TransformRendererExpr, CompositeRendererExpr
from stonemason.renderer.cartographer import DummyBaseRenderer, \
    DummyTransformRenderer, DummyCompositeRenderer


class TestBaseRendererExpr(unittest.TestCase):
    def setUp(self):
        self.renderer_expr = BaseRendererExpr(
            name='test', renderer_type='dummy')

    def test_name(self):
        self.assertEqual('test', self.renderer_expr.name)

    def test_repr(self):
        self.assertEqual(
            "BaseRendererExpr(name='test')", repr(self.renderer_expr))

    def test_interpret(self):
        self.assertIsInstance(
            self.renderer_expr.interpret(), DummyBaseRenderer)


class TestTransformRendererExpr(unittest.TestCase):
    def setUp(self):
        child = BaseRendererExpr(
            name='test', renderer_type='dummy')

        self.renderer_expr = TransformRendererExpr(
            name='test', child=child, renderer_type='dummy')

    def test_name(self):
        self.assertEqual('test', self.renderer_expr.name)

    def test_repr(self):
        self.assertEqual(
            "TransformRendererExpr(name='test', child=BaseRendererExpr(name='test'))",
            repr(self.renderer_expr))

    def test_interpret(self):
        self.assertIsInstance(
            self.renderer_expr.interpret(), DummyTransformRenderer)


class TestCompositeRendererExpr(unittest.TestCase):
    def setUp(self):
        child1 = BaseRendererExpr(
            name='test1', renderer_type='dummy')

        child2 = BaseRendererExpr(
            name='test2', renderer_type='dummy')

        self.renderer_expr = CompositeRendererExpr(
            name='test', children=[child1, child2], renderer_type='dummy')

    def test_name(self):
        self.assertEqual('test', self.renderer_expr.name)

    def test_repr(self):
        self.assertEqual(
            "CompositeRendererExpr(name='test', children=[BaseRendererExpr(name='test1'), BaseRendererExpr(name='test2')])",
            repr(self.renderer_expr))

    def test_interpret(self):
        self.assertIsInstance(
            self.renderer_expr.interpret(), DummyCompositeRenderer)
