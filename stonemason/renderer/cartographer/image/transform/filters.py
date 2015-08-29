# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.transform.filters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of render nodes that performs image filter operation.
"""
__author__ = 'ray'
__date__ = '8/7/15'

from PIL import ImageFilter

from stonemason.renderer.engine.rendernode import TransformNode
from stonemason.renderer.engine.context import RenderContext

from ..feature import ImageFeature

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
    """Min Filter

    The `MinFilter` filters a image feature with a min kernel.

    :param name: a string literal that identifies the node
    :type name: str

    :param node: source render node.
    :type nodes: :class:`stonemason.renderer.engine.RenderNode`

    :param size: kernel size
    :type size: int

    """
    def __init__(self, name, node, size=3):
        image_filter = ImageFilter.MedianFilter(size)
        _FilterNode.__init__(self, name, node, image_filter)
