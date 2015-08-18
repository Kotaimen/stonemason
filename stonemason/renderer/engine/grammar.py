# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from .rendernode import NullTermNode
from .factory import RenderNodeFactory
from .exceptions import InvalidToken, SourceNotFound


class Token(object):  # pragma: no cover
    """Abstract Token Interface"""

    def __init__(self, name, prototype, **parameters):
        self._name = name
        self._prototype = prototype
        self._parameters = parameters

    @property
    def name(self):
        return self._name

    @property
    def prototype(self):
        return self._prototype

    @property
    def parameters(self):
        return self._parameters

    def __repr__(self):
        return '%s(name=%r, parameters=%r)' % (
            self.__class__.__name__, self.name, self.parameters)


class TermToken(Token):
    """Layer Token

    A basic terminal token that represents a layer .
    """
    pass


class TransformToken(Token):
    """Transform Token

    Operational token that transform a layer.
    """

    def __init__(self, name, prototype, source, **parameters):
        Token.__init__(self, name, prototype, **parameters)
        self._source = source

    @property
    def source(self):
        return self._source


class CompositeToken(Token):
    """Composite Token

    Operational token that compose a group of layers.
    """

    def __init__(self, name, prototype, sources, **parameters):
        Token.__init__(self, name, prototype, **parameters)
        assert isinstance(sources, list)
        self._sources = sources

    @property
    def sources(self):
        return self._sources


class DictTokenizer(object):
    """Dictionary-like Expression Tokenizer

    A tokenizer that tokenize a dictionary-like expression.
    """

    def __init__(self, expression):
        assert isinstance(expression, dict)
        self._expression = expression

    def _is_token(self, expr):
        return isinstance(expr, dict) and 'prototype' in expr \
               and expr['prototype'] is not None

    def _is_terminal_token(self, expr):
        return 'source' not in expr and 'sources' not in expr

    def _is_transform_token(self, expr):
        return 'source' in expr and 'sources' not in expr

    def _is_composite_token(self, expr):
        return 'sources' in expr and 'source' not in expr

    def next_token(self, start='root'):
        expr = self._expression.get(start)
        if expr is None:
            # stop iteration
            raise StopIteration

        if not self._is_token(expr):
            raise InvalidToken(start)

        name = start
        parameters = dict(expr)
        prototype = parameters.pop('prototype', None)

        if self._is_terminal_token(expr):
            yield TermToken(name, prototype, **parameters)

        elif self._is_transform_token(expr):
            source_name = parameters.pop('source')
            for t in self.next_token(start=source_name):
                yield t

            yield TransformToken(name, prototype, source_name, **parameters)

        elif self._is_composite_token(expr):
            source_names = parameters.pop('sources')
            for source_name in source_names:
                for t in self.next_token(start=source_name):
                    yield t

            yield CompositeToken(name, prototype, source_names, **parameters)

        else:
            raise InvalidToken(start)


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
                    raise SourceNotFound

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
                        raise SourceNotFound
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
                # Should not reach here
                raise NotImplementedError

        try:
            node = stack.pop()
        except IndexError:
            return NullTermNode('empty')
        else:
            return node