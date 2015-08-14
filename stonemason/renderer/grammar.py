# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from .tokenizer import TermToken, TransformToken, CompositeToken, DictTokenizer
from .expression import NullNode, RenderNodeFactory


class RenderGrammar(object):
    """Expression Grammar for Rendering

    The `RenderGrammar` takes a layer tokenizer and parses into a layer
    renderer.
    """

    def __init__(self, tokenizer, start='root', factory=None):
        assert isinstance(tokenizer, DictTokenizer)
        assert isinstance(factory, RenderNodeFactory)
        self._tokenizer = tokenizer
        self._start = start
        self._factory = factory

    def parse(self):
        stack = list()

        for token in self._tokenizer.next_token(start=self._start):
            if isinstance(token, TransformToken):
                source_node = stack.pop()
                if source_node is None:
                    raise ValueError

                node = self._factory.create_transform_node(
                    token.name,
                    token.prototype,
                    source_node,
                    **token.parameters)

                stack.append(node)

            elif isinstance(token, CompositeToken):
                source_nodes = list()
                for i in token.sources:
                    source_node = stack.pop()
                    if source_node is None:
                        raise ValueError
                    source_nodes.append(source_node)

                node = self._factory.create_composite_node(
                    token.name,
                    token.prototype,
                    source_nodes,
                    **token.parameters)

                stack.append(node)

            elif isinstance(token, TermToken):
                node = self._factory.create_terminal_node(
                    token.name,
                    token.prototype,
                    **token.parameters)

                stack.append(node)
            else:
                raise ValueError

        try:
            node = stack.pop()
        except IndexError:
            return NullNode('empty')
        else:
            return node
