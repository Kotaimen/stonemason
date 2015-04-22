# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from PIL import Image

from stonemason.renderer.context import RenderContext
from stonemason.renderer.grammar import RenderGrammar
from stonemason.renderer.tokenizer import DictTokenizer

from tests import ImageTestCase


class TestGrammar(ImageTestCase):
    def test(self):
        e = {
            'root': {
                'prototype': 'pil.blend.alpha',
                'sources': ['l1', 'l2'],

            },
            'l1': {
                'prototype': 'pil.invert',
                'source': 'l3'
            },
            'l2': {
                'prototype': 'pil.black',
            },
            'l3': {
                'prototype': 'pil.black',
            }
        }

        tok = DictTokenizer(e)
        g = RenderGrammar(tok)

        layer = g.parse()

        context = RenderContext(
            'EPSG:3857', (-180, -85, 180, 85), (256, 256))

        feature = layer.render(context)

        expected = Image.new('RGB', (256, 256), (127, 127, 127))

        self.assertImageEqual(feature.data, expected)

