# -*- encoding: utf-8 -*-
"""
    stonemason.mason.config.grammar
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the grammar of different config format.

"""

import json

__all__ = ['JsonGrammar', ]


class GrammarError(Exception):
    pass


class Grammar(object):
    """Basic Grammar Parser

    A Grammar Parser analyzes and translates an expression
    into a dict.
    """

    def parse(self, expr):
        """Parse a expression into a dict

        Interface for subclass to override.

        :param expr: An expression string.
        :type expr: str
        :return: A dict contains the parsed result.
        :returns: dict
        """
        raise NotImplementedError


class JsonGrammar(Grammar):
    """Json Grammar Parser

    The json parser loads a json and returns a dict.
    """

    def parse(self, expr):
        """Parse a json into a dict

        :param expr: An expression string.
        :type expr: str
        :return: A dict contains the parsed result.
        :returns: dict
        """
        try:
            return json.loads(expr)
        except ValueError:
            raise GrammarError
