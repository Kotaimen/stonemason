# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

from .dummy import DummyBaseRenderer, DummyTransformRenderer, \
    DummyCompositeRenderer

try:
    from .mapnik_ import MapnikMapRenderer
    #: A boolean indicates whether Mapnik is available.
    HAS_MAPNIK = True
except ImportError:
    HAS_MAPNIK = False

    class MapnikMapRenderer:
        pass


class UnknownRendererType(Exception):
    pass


BASE_RENDERERS = {
    'dummy': DummyBaseRenderer,
    'image.mapnik': MapnikMapRenderer
}


class BaseRendererFactory(object):
    def create(self, name, renderer_type, **renderer_parameters):
        try:
            setup = BASE_RENDERERS[renderer_type]
        except KeyError:
            raise UnknownRendererType(renderer_type)

        return setup(name, **renderer_parameters)


TRANSFORM_RENDERERS = {
    'dummy': DummyTransformRenderer,
}


class TransformRendererFactory(object):
    def create(self, name, child, renderer_type, **renderer_parameters):
        try:
            setup = TRANSFORM_RENDERERS[renderer_type]
        except KeyError:
            raise UnknownRendererType(renderer_type)

        return setup(name, child, **renderer_parameters)


COMPOSITOR_RENDERERS = {
    'dummy': DummyCompositeRenderer,
}


class CompositeRendererFactory(object):
    def create(self, name, children, renderer_type, **renderer_parameters):
        try:
            setup = COMPOSITOR_RENDERERS[renderer_type]
        except KeyError:
            raise UnknownRendererType(renderer_type)

        return setup(name, children, **renderer_parameters)
