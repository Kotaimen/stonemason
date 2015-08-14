# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

from .exceptions import LexicalError, InvalidNodeConfig, NodeConfigNotFound


class AbstractToken(object):  # pragma: no cover
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


class TermToken(AbstractToken):
    """Layer Token

    A basic terminal token that represents a layer .
    """
    pass


class TransformToken(AbstractToken):
    """Transform Token

    Operational token that transform a layer.
    """

    def __init__(self, name, prototype, source, **parameters):
        AbstractToken.__init__(self, name, prototype, **parameters)
        self._source = source

    @property
    def source(self):
        return self._source


class CompositeToken(AbstractToken):
    """Composite Token

    Operational token that compose a group of layers.
    """

    def __init__(self, name, prototype, sources, **parameters):
        AbstractToken.__init__(self, name, prototype, **parameters)
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

    def next_token(self, start='root'):
        token = self._expression.get(start)
        if token is None:
            return

        if not isinstance(token, dict):
            raise InvalidNodeConfig(start)

        parameters = dict(token)

        name = start
        prototype = parameters.pop('prototype', None)

        if 'source' in token:
            source_name = parameters.pop('source')
            for t in self.next_token(start=source_name):
                yield t

            yield TransformToken(name, prototype, source_name, **parameters)

        elif 'sources' in token:
            source_names = parameters.pop('sources')
            for source_name in source_names:
                for t in self.next_token(start=source_name):
                    yield t

            yield CompositeToken(name, prototype, source_names, **parameters)

        else:
            yield TermToken(name, prototype, **parameters)

