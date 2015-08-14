# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from .grammar import RenderGrammar
from .context import RenderContext
from .tokenizer import DictTokenizer

from .expression import ImageNodeFactory

from .cartographer import register_image_render_node


class MasonRenderer(object):
    def __init__(self, expression):
        factory = ImageNodeFactory()
        register_image_render_node(factory)

        tokenizer = DictTokenizer(expression)

        grammar = RenderGrammar(tokenizer, start='root', factory=factory)
        self._renderer = grammar.parse()

    def render(self, context):
        assert isinstance(context, RenderContext)
        return self._renderer.render(context)
