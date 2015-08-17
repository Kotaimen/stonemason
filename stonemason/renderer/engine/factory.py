# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/17/15'




class RenderNodeFactory(object):
    def __init__(self):
        self._register = dict()

    def _lookup(self, prototype):
        init = self._register.get(prototype)
        if init is None:
            raise ValueError('Unknown prototype: "%s"!' % prototype)
        return init

    def create_terminal_node(self, name, prototype, **parameters):
        init = self._lookup(prototype)
        return init(name, **parameters)

    def create_transform_node(self, name, prototype, source, **parameters):
        init = self._lookup(prototype)
        return init(name, node=source, **parameters)

    def create_composite_node(self, name, prototype, sources, **parameters):
        init = self._lookup(prototype)
        return init(name, nodes=sources, **parameters)

