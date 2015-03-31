# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/12/15'

from stonemason.pyramid import Pyramid, MetaTile, MetaTileIndex
from stonemason.provider.formatbundle import FormatBundle
from stonemason.renderer.map import RenderContext, ImageMapRenderer


class MetaTileRenderer(object):
    def render_metatile(self, meta_index):
        raise NotImplementedError


class NullMetaTileRenderer(MetaTileRenderer):
    def render_metatile(self, meta_index):
        return None


class ImageMetaTileRenderer(MetaTileRenderer):
    def __init__(self, pyramid, bundle, image_renderer):
        assert isinstance(pyramid, Pyramid)
        assert isinstance(bundle, FormatBundle)
        assert isinstance(image_renderer, ImageMapRenderer)
        MetaTileRenderer.__init__(self)
        self._pyramid = pyramid
        self._bundle = bundle
        self._renderer = image_renderer

    def render_metatile(self, meta_index):
        assert isinstance(meta_index, MetaTileIndex)

        context = RenderContext(
            pyramid=self._pyramid,
            map_bbox=None,
            map_size=meta_index.stride * 256
        )

        im = self._renderer.image(context)
        if im is None:
            return None

        parameters = self._bundle.tile_format.parameters

        metatile = MetaTile(index=meta_index, data=im.tostring(**parameters))

        return metatile


class RasterMetaTileRenderer(MetaTileRenderer):
    pass


class VectorMetaTileRenderer(MetaTileRenderer):
    pass

