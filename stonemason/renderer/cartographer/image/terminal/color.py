# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

from PIL import Image, ImageColor

from stonemason.renderer.expression import TermNode
from stonemason.renderer.feature import ImageFeature
from stonemason.renderer.context import RenderContext

__all__ = ['Color']


class Color(TermNode):
    def __init__(self, name, color='#000'):
        TermNode.__init__(self, name)
        self._color = ImageColor.getrgb(color)

    def render(self, context):
        assert isinstance(context, RenderContext)

        pil_image = Image.new('RGBA', context.map_size, color=self._color)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature
