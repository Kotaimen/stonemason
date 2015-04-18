# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/12/15'

import io

from PIL import Image

from stonemason.pyramid import Pyramid, MetaTile, MetaTileIndex
from stonemason.formatbundle import FormatBundle
from stonemason.renderer.map import RenderContext, ImageMapRenderer
from stonemason.pyramid.geo import TileMapSystem


class MetaTileRenderer(object):

    @property
    def pyramid(self):
        raise NotImplementedError

    @property
    def tms(self):
        raise NotImplementedError

    @property
    def bundle(self):
        raise NotImplementedError

    def render_metatile(self, meta_index):
        raise NotImplementedError


class NullMetaTileRenderer(MetaTileRenderer):

    @property
    def pyramid(self):
        return Pyramid()

    @property
    def tms(self):
        return TileMapSystem(Pyramid())

    @property
    def bundle(self):
        return FormatBundle()

    def render_metatile(self, meta_index):
        return None


class ImageMetaTileRenderer(MetaTileRenderer):
    def __init__(self, pyramid, bundle, image_renderer):
        assert isinstance(pyramid, Pyramid)
        assert isinstance(bundle, FormatBundle)
        assert isinstance(image_renderer, ImageMapRenderer)
        MetaTileRenderer.__init__(self)
        self._pyramid = pyramid
        self._tms = TileMapSystem(pyramid)
        self._bundle = bundle
        self._renderer = image_renderer

    @property
    def pyramid(self):
        return self._pyramid

    @property
    def tms(self):
        return self._tms

    @property
    def bundle(self):
        return self._bundle

    def render_metatile(self, meta_index):
        assert isinstance(meta_index, MetaTileIndex)

        context = RenderContext(
            pyramid=self._tms.pyramid,
            map_bbox=self._tms.calc_tile_envelope(meta_index),
            map_size=(meta_index.stride * 256, meta_index.stride * 256),
        )

        im = self._renderer.image(context)
        if im is None:
            return None

        assert isinstance(im, Image.Image)

        buffer = io.BytesIO()
        im.save(buffer,
                format=self._bundle.tile_format.format,
                parameters=self._bundle.tile_format.parameters)

        data = buffer.getvalue()
        del buffer

        metatile = MetaTile(
            index=meta_index,
            mimetype=self._bundle._tile_format.mimetype,
            data=data,
        )

        return metatile


class RasterMetaTileRenderer(MetaTileRenderer):
    pass


class VectorMetaTileRenderer(MetaTileRenderer):
    pass

