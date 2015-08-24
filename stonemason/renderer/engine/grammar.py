# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.grammar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Grammar components of render expression.
"""

__author__ = 'ray'
__date__ = '4/20/15'

from .rendernode import NullTermNode
from .factory import RenderNodeFactory
from .exceptions import InvalidToken, SourceNotFound


class Token(object):
    """Abstract Grammar Token Interface

    A `Token` defines the basic interface of a component in the render
    expression.

    A `Token` has a name that could be referenced by other tokens as their
    source。And it also has a prototype that indicate what kind of render node
    it represents, and parameters that used to setup the node.

    For example:

    .. code-block:: javascript

        "my_token_name": {
            "prototype": "blabla",
            "param1": "value1",
            "param2": "value2"
        }


    :param name: a string literal used to identify the render node.
    :type name: str

    :param prototype: a string literal that represents the kind of render node.
    :type prototype: str

    :param parameters: attributes that used to setup the render node.
    :type parameters: dict

    """

    def __init__(self, name, prototype, **parameters):
        self._name = name
        self._prototype = prototype
        self._parameters = parameters

    @property
    def name(self):
        """Get name of the token."""
        return self._name

    @property
    def prototype(self):
        """Get prototype of the token."""
        return self._prototype

    @property
    def parameters(self):
        """Get parameters of the token."""
        return self._parameters

    def __repr__(self):
        return '%s(name=%r, parameters=%r)' % (
            self.__class__.__name__, self.name, self.parameters)


class TermToken(Token):
    """Terminal Token

    A `TermToken` represents a leaf node in the render tree.

    For example:

    .. code-block:: javascript

        "my_term_token_name": {
            "prototype": "terminal_node_prototype",
            "param1": "value1",
            "param2": "value2"
        }

    """
    pass


class TransformToken(Token):
    """Transform Token

    A `TransformToken` represents a render node that preform transform operation
     on data of source node.

    For example:

    .. code-block:: javascript

        "my_transform_token_name": {
            "prototype": "transform_node_prototype",
            "source": "another_token_name",
            "param1": "value1",
            "param2": "value2"
        }

    """

    def __init__(self, name, prototype, source, **parameters):
        Token.__init__(self, name, prototype, **parameters)
        self._source = source

    @property
    def source(self):
        """Get source render node."""
        return self._source


class CompositeToken(Token):
    """Composite Token

     A `CompositeToken` represents a render node that preform composite
     operation on data of source nodes.

     For example:

    .. code-block:: javascript

        "my_composite_token_name": {
            "prototype": "composite_node_prototype",
            "sources": ["one_token_name", "another_token_name"],
            "param1": "value1",
            "param2": "value2"
        }

    """

    def __init__(self, name, prototype, sources, **parameters):
        Token.__init__(self, name, prototype, **parameters)
        assert isinstance(sources, list)
        self._sources = sources

    @property
    def sources(self):
        """Get source render node."""
        return self._sources


class DictTokenizer(object):
    """Dictionary-like Expression Tokenizer

    A tokenizer that tokenize a dictionary-like expression.
    """

    def __init__(self, expression):
        assert isinstance(expression, dict)
        self._expression = expression

    def _is_token(self, expr):
        """Check if the given expression is a valid token."""
        return isinstance(expr, dict) and 'prototype' in expr \
               and expr['prototype'] is not None

    def _is_terminal_token(self, expr):
        """Check if the given expression is a terminal token."""
        return 'source' not in expr and 'sources' not in expr

    def _is_transform_token(self, expr):
        """Check if the given expression is a transform token"""
        return 'source' in expr and 'sources' not in expr

    def _is_composite_token(self, expr):
        """Check if the given expression is a composite token"""
        return 'sources' in expr and 'source' not in expr

    def next_token(self, start='root'):
        """Get next token from ``start`` node

        :param start: name of the start token.
        :type start: str

        """
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

    The `RenderGrammar` parses render expression into a tree of render node. If
    no valid render node is found, it returns a empty node which returns
    ``None``.

    :param tokenizer: a tokenizer that breaks render expression into tokens.
    :type tokenizer: :class:`~stonemason.renderer.engine.DictTokenizer`

    :param start: name of the root node.
    :type start: str

    :param factory: a instance of render node factory that create render node.
    :type factory: :class:`~stonemason.renderer.engine.RenderNodeFactory`

    """

    def __init__(self, tokenizer, start='root', factory=None):
        assert isinstance(tokenizer, DictTokenizer)
        assert isinstance(factory, RenderNodeFactory)
        self._tokenizer = tokenizer
        self._start = start
        self._factory = factory

    def parse(self):
        """Parse render expression into render node tree

        :return: return a render node tree
        :rtype: :class:`~stonemason.renderer.engine.RenderNode`
        """
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
