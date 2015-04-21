# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from .grammar import RenderGrammar
from .context import RenderContext
from .tokenizer import DictTokenizer


class MasonRenderer(object):
    def __init__(self, expression):
        grammar = RenderGrammar(DictTokenizer(expression), start='root')
        self._renderer = grammar.parse()

    def render(self, context):
        assert isinstance(context, RenderContext)
        return self._renderer.render(context)
