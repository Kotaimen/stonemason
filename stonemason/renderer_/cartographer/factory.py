# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from ..exceptions import UnknownPrototype

from .imagery import IMAGERY_LAYERS


class LayerFactory(object):
    def create_terminal_layer(self, name, prototype, **parameters):
        init = IMAGERY_LAYERS.get(prototype)
        if init is None:
            raise UnknownPrototype(prototype)

        return init(name, **parameters)


    def create_transform_layer(self, name, prototype, source, **parameters):
        init = IMAGERY_LAYERS.get(prototype)
        if init is None:
            raise UnknownPrototype(prototype)

        return init(name, layer=source, **parameters)

    def create_composite_layer(self, name, prototype, sources, **parameters):
        init = IMAGERY_LAYERS.get(prototype)
        if init is None:
            raise UnknownPrototype(prototype)

        return init(name, layers=sources, **parameters)

