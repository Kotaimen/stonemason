# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/22/15'


class DesignError(Exception):
    pass


class LayerRendererMissing(DesignError):
    pass


class LayerExprNotFound(DesignError):
    pass
