# -*- encoding: utf-8 -*-
"""
    stonemason.mason.config.parser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the Parser of stonemason config.

"""
from . import grammar


class ConfigParserError(Exception):
    pass


class UnsupportedGrammar(ConfigParserError):
    pass


class ConfigParser(object):
    """Config Parser

    A ConfigParser reads config from a file or stream
    and returns a parsed tree-like object.
    """

    def parse(self, expr):
        """Parse an expression

        Find a proper grammar parser to parse an expression to dict.

        :param expr: A string expression.
        :type expr: str
        :return: A dict object.
        :returns: dict
        """

        for g_cls in grammar.Grammar.__subclasses__():
            try:
                g = g_cls()
                return g.parse(expr)
            except grammar.GrammarError:
                continue

        else:
            raise UnsupportedGrammar(
                'Can not find proper grammar to parse!')

