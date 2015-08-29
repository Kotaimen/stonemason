# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from stonemason.renderer.engine.grammar import RenderGrammar, DictTokenizer
from stonemason.renderer.engine.context import RenderContext

from stonemason.renderer.cartographer import ImageNodeFactory


class MasonRenderer(object):
    def __init__(self, expression):
        factory = ImageNodeFactory()
        tokenizer = DictTokenizer(expression)
        grammar = RenderGrammar(tokenizer, start='root', factory=factory)

        self._renderer = grammar.parse()

    def render(self, context):
        assert isinstance(context, RenderContext)
        return self._renderer.render(context)
