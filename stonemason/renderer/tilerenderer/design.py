# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/22/15'

from stonemason.renderer.cartographer import BaseRendererFactory, \
    TransformRendererFactory, CompositeRendererFactory

from .exceptions import LayerExprNotFound, LayerRendererMissing


class RendererExpr(object):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def interpret(self):
        raise NotImplementedError

    def __repr__(self):
        return '%s(name=%r)' % self.name


class BaseRendererExpr(RendererExpr):
    def __init__(self, name, renderer_type, **renderer_parameters):
        RendererExpr.__init__(self, name)
        self._renderer_type = renderer_type
        self._renderer_parameters = renderer_parameters

    def interpret(self):
        renderer = BaseRendererFactory().create(
            self.name, self._renderer_type, **self._renderer_parameters)
        return renderer

    def __repr__(self):
        return '%s(name=%r)' % (self.__class__.__name__, self.name)


class TransformRendererExpr(RendererExpr):
    def __init__(self, name, child, renderer_type, **renderer_parameters):
        RendererExpr.__init__(self, name)
        self._child = child
        self._renderer_type = renderer_type
        self._renderer_parameters = renderer_parameters

    def interpret(self):
        renderer = TransformRendererFactory().create(
            self.name, self._child, self._renderer_type,
            **self._renderer_parameters)
        return renderer

    def __repr__(self):
        return '%s(name=%r, child=%r)' % (
            self.__class__.__name__, self.name, self._child)


class CompositeRendererExpr(RendererExpr):
    def __init__(self, name, children, renderer_type, **renderer_parameters):
        RendererExpr.__init__(self, name)
        self._children = children
        self._renderer_type = renderer_type
        self._renderer_parameters = renderer_parameters

    def interpret(self):
        renderer = CompositeRendererFactory().create(
            self.name, self._children, self._renderer_type,
            **self._renderer_parameters
        )
        return renderer

    def __repr__(self):
        return '%s(name=%r, children=%r)' % (
            self.__class__.__name__, self.name, self._children)


class RendererExprParser(object):
    def __init__(self, pyramid):
        self._pyramid = pyramid

    def parse_from_dict(self, d, root_name='root'):
        assert isinstance(d, dict)

        expr = d.get(root_name)
        if expr is None or not isinstance(expr, dict):
            raise LayerExprNotFound(root_name)

        renderer_type = expr.pop('type')
        if renderer_type is None:
            raise LayerRendererMissing

        if 'sources' in expr:
            children = list()
            for child_name in expr.pop('sources'):
                node = self.parse_from_dict(d, child_name)
                children.append(node)

            return CompositeRendererExpr(
                root_name, children, renderer_type, **expr)
        elif 'source' in expr:
            child_name = expr.pop('source')
            child = self.parse_from_dict(d, child_name)

            return TransformRendererExpr(
                root_name, child, renderer_type, **expr)

        else:
            return BaseRendererExpr(root_name, renderer_type, **expr)
