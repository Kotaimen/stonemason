# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/19/15'

from stonemason.renderer.cartographer import MapnikRenderer


class MapRendererFactory(object):
    def create_renderer(self, prototype, name, **kwargs):
        raise NotImplementedError


class ImageMapRendererFactory(MapRendererFactory):
    IMAGE_MAP_RENDERERS = {
        'mapnik': MapnikRenderer
    }

    def create_renderer(self, prototype, name, **kwargs):
        init = self.IMAGE_MAP_RENDERERS.get(prototype)
        if init is None:
            raise ValueError('Invalid layer type %s' % prototype)

        return init(name=name, **kwargs)
