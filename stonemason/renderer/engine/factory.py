# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/17/15'

from .rendernode import RenderNode
from .exceptions import UnknownPrototype, DependencyNotFound


class RenderNodeFactory(object):
    def __init__(self):
        self._register = dict()

    def _lookup(self, prototype):
        try:
            init = self._register[prototype]
        except KeyError:
            raise UnknownPrototype('"%s"' % prototype)
        if init is None:
            raise DependencyNotFound(
                """Missing dependencies for: "%s"!""" % prototype)
        return init

    def register_node(self, prototype, node_class):
        assert node_class is None or issubclass(node_class, RenderNode)
        self._register[prototype] = node_class

    def create_terminal_node(self, name, prototype, **parameters):
        init = self._lookup(prototype)
        return init(name, **parameters)

    def create_transform_node(self, name, prototype, source, **parameters):
        init = self._lookup(prototype)
        return init(name, node=source, **parameters)

    def create_composite_node(self, name, prototype, sources, **parameters):
        init = self._lookup(prototype)
        return init(name, nodes=sources, **parameters)
