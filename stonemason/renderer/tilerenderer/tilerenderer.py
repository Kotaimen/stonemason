# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/12/15'

from stonemason.provider.formatbundle import MapType
from stonemason.pyramid import Pyramid, MetaTile, MetaTileIndex
from stonemason.renderer.map import ImageMapRenderer, RenderContext

from .design import RendererExprParser


class MetaTileRenderer(object):
    def __init__(self, pyramid):
        assert isinstance(pyramid, Pyramid)
        self._pyramid = pyramid

    def render_metatile(self, metatile_index):
        raise NotImplementedError


class ImageMetaTileRenderer(MetaTileRenderer):
    def __init__(self, pyramid, image_renderer):
        assert isinstance(image_renderer, ImageMapRenderer)
        MetaTileRenderer.__init__(self, pyramid)
        self._renderer = image_renderer

    def render_metatile(self, metatile_index):
        assert isinstance(metatile_index, MetaTileIndex)

        context = RenderContext(
            pyramid=self._pyramid,
            target_bbox=None,
            target_size=metatile_index.stride * 256
        )

        im = self._renderer.image(context)

        metatile = MetaTile(index=metatile_index, data=im.tostring())

        return metatile


class RasterMetaTileRenderer(MetaTileRenderer):
    pass


class VectorMetaTileRenderer(MetaTileRenderer):
    pass


class MetaTileRendererBuilder(object):
    def build(self, theme):
        maptype = MapType(theme.maptype)
        pyramid = Pyramid(**theme.pyramid.attributes)

        if maptype.type == 'image':
            renderer = RendererExprParser(pyramid).parse_from_dict(
                theme.design.layers, 'root').interpret()
            return ImageMetaTileRenderer(pyramid, renderer)
        else:
            raise NotImplementedError
