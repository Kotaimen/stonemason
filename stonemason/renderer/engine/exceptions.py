# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'


class RendererError(Exception):
    pass


class DependencyNotFound(RuntimeError):
    pass


class TokenError(RendererError):
    pass


class GrammarError(RendererError):
    pass


class InvalidToken(TokenError):
    pass


class SourceNotFound(GrammarError):
    pass


class UnknownPrototype(GrammarError):
    pass
