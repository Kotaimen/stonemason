# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'


class RendererError(Exception):
    pass


class LexicalError(RendererError):
    pass


class LayerConfigNotFound(LexicalError):
    pass


class InvalidLayerConfig(LexicalError):
    pass


class SemanticError(RendererError):
    pass


class UnknownPrototype(SemanticError):
    pass
