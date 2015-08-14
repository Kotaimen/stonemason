# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from PIL import Image

from stonemason.renderer.context import RenderContext
from stonemason.renderer.grammar import RenderGrammar
from stonemason.renderer.tokenizer import DictTokenizer
from stonemason.renderer.expression import ImageNodeFactory
from stonemason.renderer.cartographer import register_image_render_node

from tests import ImageTestCase


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
        register_image_render_node(factory)

        g = RenderGrammar(tokenizer, start='root', factory=factory)

        layer = g.parse()

        context = RenderContext(
            'EPSG:3857', (-180, -85, 180, 85), (256, 256))

        feature = layer.render(context)

        expected = Image.new('RGBA', (256, 256), '#0f0')

        self.assertImageEqual(feature.data, expected)
