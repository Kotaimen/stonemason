# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/19/15'


class AbstractLayer(object):  # pragma: no cover
    """Abstract Layer Renderer"""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def render(self, context):
        raise NotImplementedError


class TerminalLayer(AbstractLayer):  # pragma: no cover
    """Abstract Terminal Layer Renderer"""

    def __repr__(self):
        return '%s(name=%r)' % (self.__class__.__name__, self.name)


class TransformLayer(AbstractLayer):  # pragma: no cover
    """Abstract Transform Layer Renderer"""

    def __init__(self, name, layer):
        AbstractLayer.__init__(self, name)
        assert isinstance(layer, AbstractLayer)
        self._layer = layer

    def __repr__(self):
        return '%s(name=%r, %r)' % (
            self.__class__.__name__, self.name, self._layer)


class CompositeLayer(AbstractLayer):  # pragma: no cover
    """Abstract Composite Layer Renderer"""

    def __init__(self, name, layers):
        AbstractLayer.__init__(self, name)
        self._layers = layers

    def __repr__(self):
        components = ', '.join('%r' % l for l in self._layers)
        return '%s(name=%r, %s)' % (
            self.__class__.__name__, self.name, components)


class ImageryLayer(TerminalLayer):  # pragma: no cover
    """Abstract Terminal Imagery Layer Renderer

    A Imagery Layer Renderer returns a `ImageFeature`.
    """
    pass


class VectorLayer(TerminalLayer):  # pragma: no cover
    """Abstract Terminal Imagery Layer Renderer

    A Vector Layer Renderer returns a `VectorFeature`.
    """
    pass


class RasterLayer(TerminalLayer):  # pragma: no cover
    """Abstract Terminal Imagery Layer Renderer

    A Raster Layer Renderer returns a `RasterFeature`.
    """
    pass
