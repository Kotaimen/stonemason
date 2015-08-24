# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.context
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions of render engine.
"""

__author__ = 'ray'
__date__ = '4/21/15'


class RendererError(Exception):
    """Base Renderer Error

    Base Exception of Mason Renderer Engine.
    """
    pass


class DependencyNotFound(RendererError):
    """Dependency Not Found

    Dependent module or executable for a specific render node is missing.
    """
    pass


class TokenError(RendererError):
    """Token Error

    Base lexical error in render expression.
    """
    pass


class InvalidToken(TokenError):
    """Invalid Token

    Cannot derived a token from the expression.
    """
    pass


class GrammarError(RendererError):
    """Grammar Error

    Base grammar error in render expression.
    """
    pass


class SourceNotFound(GrammarError):
    """Input Render Source Not Found

    Missing input render node(s).
    """
    pass


class UnknownPrototype(GrammarError):
    """Unknown Render Node Prototype

    Unknown prototype is specified in the render expression.
    """
    pass
