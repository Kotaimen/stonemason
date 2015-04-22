# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from .cartographer import LayerFactory, EmptyLayer
from .tokenizer import LayerToken, TransformToken, CompositeToken, DictTokenizer


class RenderGrammar(object):
    """Expression Grammar for Rendering

    The `RenderGrammar` takes a layer tokenizer and parses into a layer
    renderer.
    """

    def __init__(self, tokenizer, start='root', factory=None):
        assert isinstance(tokenizer, DictTokenizer)
        self._tokenizer = tokenizer
        self._start = start
        self._factory = LayerFactory()

    def parse(self):
        stack = list()

        for token in self._tokenizer.next_token(start=self._start):
            if isinstance(token, TransformToken):
                source_layer = stack.pop()
                if source_layer is None:
                    raise ValueError

                layer = self._factory.create_transform_layer(
                    token.name,
                    token.prototype,
                    source_layer,
                    **token.parameters)

                stack.append(layer)

            elif isinstance(token, CompositeToken):
                source_layers = list()
                for i in token.sources:
                    source_layer = stack.pop()
                    if source_layer is None:
                        raise ValueError
                    source_layers.append(source_layer)

                layer = self._factory.create_composite_layer(
                    token.name,
                    token.prototype,
                    source_layers,
                    **token.parameters)

                stack.append(layer)

            elif isinstance(token, LayerToken):
                layer = self._factory.create_terminal_layer(
                    token.name,
                    token.prototype,
                    **token.parameters)

                stack.append(layer)
            else:
                raise ValueError

        try:
            layer = stack.pop()
        except IndexError:
            return EmptyLayer('empty')
        else:
            return layer


