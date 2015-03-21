# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/17/15'

from stonemason.pyramid import MetaTileIndex, MetaTile
from stonemason.renderer.map import RenderContext


class MapSource(object):
    def __init__(self, pyramid, renderer):
        self._pyramid = pyramid
        self._renderer = renderer

    def render_metatile(self, metatile_index):
        raise NotImplementedError


class ImageMapSource(MapSource):
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
