# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

from PIL import ImageFilter

from stonemason.renderer.expression import TransformNode
from stonemason.renderer.feature import ImageFeature
from stonemason.renderer.context import RenderContext

__all__ = ['MinFilter']


class _FilterNode(TransformNode):
    def __init__(self, name, node, image_filter):
        TransformNode.__init__(self, name, node)
        self._filter = image_filter

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._node.render(context).data

        pil_image = src.filter(self._filter)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature


class MinFilter(_FilterNode):
    def __init__(self, name, node, size=3):
        image_filter = ImageFilter.MedianFilter(size)
        _FilterNode.__init__(self, name, node, image_filter)
