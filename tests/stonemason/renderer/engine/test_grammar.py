# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

import unittest

from PIL import Image

from stonemason.renderer.engine.context import RenderContext
from stonemason.renderer.cartographer import ImageNodeFactory
from stonemason.renderer.engine.grammar import *

from tests import ImageTestCase


class TestLayerToken(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.prototype = 'null'
        self.parameters = dict(param1=1, param2=2)
        self.token = TermToken(self.name, self.prototype, param1=1, param2=2)

    def test_name(self):
        self.assertEqual(self.name, self.token.name)

    def test_prototype(self):
        self.assertEqual(self.prototype, self.token.prototype)

    def test_parameters(self):
        self.assertDictEqual(self.parameters, self.token.parameters)


class TestTransformToken(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.prototype = 'null'
        self.parameters = dict(param1=1, param2=2)
        self.source = 'source'
        self.token = TransformToken(
            self.name, self.prototype, self.source, param1=1, param2=2)

    def test_name(self):
        self.assertEqual(self.name, self.token.name)

    def test_prototype(self):
        self.assertEqual(self.prototype, self.token.prototype)

    def test_source(self):
        self.assertEqual(self.source, self.token.source)

    def test_parameters(self):
        self.assertDictEqual(self.parameters, self.token.parameters)


class TestCompositeToken(unittest.TestCase):
    def setUp(self):
        self.name = 'test'
        self.prototype = 'null'
        self.parameters = dict(param1=1, param2=2)
        self.sources = ['source1', 'source2']
        self.token = CompositeToken(
            self.name, self.prototype, self.sources, param1=1, param2=2)

    def test_name(self):
        self.assertEqual(self.name, self.token.name)

    def test_prototype(self):
        self.assertEqual(self.prototype, self.token.prototype)

    def test_sources(self):
        self.assertEqual(self.sources, self.token.sources)

    def test_parameters(self):
        self.assertDictEqual(self.parameters, self.token.parameters)


class TestTokenizer(unittest.TestCase):
    def test_empty_expr(self):
        expr = {}

        tokenizer = DictTokenizer(expr)
        self.assertListEqual(list(), list(tokenizer.next_token()))

    def test_expr_without_prototype(self):
        expr = {
            'root': {

            }
        }

        tokenizer = DictTokenizer(expr)
        token = list(tokenizer.next_token())[0]

        self.assertIsInstance(token, TermToken)
        self.assertEqual('root', token.name)
        self.assertEqual(None, token.prototype)
        self.assertDictEqual({}, token.parameters)

    def test_single_expr(self):
        expr = {
            'root': {
                'prototype': 'p1',
                'param1': 1,
                'param2': 2,
            }
        }

        tokenizer = DictTokenizer(expr)

        tokens = list(tokenizer.next_token())
        self.assertEqual(1, len(tokens))

        token = tokens[0]
        self.assertIsInstance(token, TermToken)
        self.assertEqual('root', token.name)
        self.assertEqual('p1', token.prototype)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)

    def test_transform_expr(self):
        expr = {
            's1': {
                'prototype': 'p1',
                'param1': 1,
                'param2': 2,
            },
            'root': {
                'prototype': 't1',
                'source': 's1',
                'param1': 1,
                'param2': 2,
            }
        }

        tokenizer = DictTokenizer(expr)

        tokens = list(tokenizer.next_token())
        self.assertEqual(2, len(tokens))

        token = tokens[0]
        self.assertIsInstance(token, TermToken)
        self.assertEqual('s1', token.name)
        self.assertEqual('p1', token.prototype)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)

        token = tokens[1]
        self.assertIsInstance(token, TransformToken)
        self.assertEqual('root', token.name)
        self.assertEqual('t1', token.prototype)
        self.assertEqual('s1', token.source)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)

    def test_composite_expr(self):
        expr = {
            's1': {
                'prototype': 'p1',
                'param1': 1,
                'param2': 2,
            },
            's2': {
                'prototype': 'p2',
                'param1': 1,
                'param2': 2,
            },
            'root': {
                'prototype': 't1',
                'sources': ['s1', 's2'],
                'param1': 1,
                'param2': 2,
            }
        }

        tokenizer = DictTokenizer(expr)

        tokens = list(tokenizer.next_token())
        self.assertEqual(3, len(tokens))

        token = tokens[0]
        self.assertIsInstance(token, TermToken)
        self.assertEqual('s1', token.name)
        self.assertEqual('p1', token.prototype)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)

        token = tokens[1]
        self.assertIsInstance(token, TermToken)
        self.assertEqual('s2', token.name)
        self.assertEqual('p2', token.prototype)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)

        token = tokens[2]
        self.assertIsInstance(token, CompositeToken)
        self.assertEqual('root', token.name)
        self.assertEqual('t1', token.prototype)
        self.assertEqual(['s1', 's2'], token.sources)
        self.assertDictEqual(dict(param1=1, param2=2), token.parameters)


class TestGrammar(ImageTestCase):
    def test_parse(self):
        e = {
            'root': {
                'prototype': 'basic.blend',
                'sources': ['c1', 'l3'],
                'alpha': 0
            },
            'c1': {
                'prototype': 'basic.blend',
                'sources': ['l1', 'l2'],
                'alpha': 1
            },
            'l1': {
                'prototype': 'basic.color',
                'color': '#00f'
            },
            'l2': {
                'prototype': 'basic.color',
                'color': '#f00'
            },
            'l3': {
                'prototype': 'basic.color',
                'color': '#0f0'
            }
        }

        tokenizer = DictTokenizer(e)

        factory = ImageNodeFactory()

        g = RenderGrammar(tokenizer, start='root', factory=factory)

        layer = g.parse()

        context = RenderContext(
            'EPSG:3857', (-180, -85, 180, 85), (256, 256))

        feature = layer.render(context)

        expected = Image.new('RGBA', (256, 256), '#0f0')

        self.assertImageEqual(feature.data, expected)
