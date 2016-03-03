# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.composite.alphacomposer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of composite render node that performs alpha blending.
"""
__author__ = 'ray'
__date__ = '8/7/15'

from PIL import Image

from stonemason.renderer.engine.rendernode import CompositeNode
from stonemason.renderer.engine.context import RenderContext

from ..feature import ImageFeature

__all__ = ['AlphaComposer']

class AlphaComposer(CompositeNode):
    """Compose two imagery sources.

    :param name: a string literal that identifies the node.
    :type name: str

    :param nodes: a list of two source render nodes.
    :type nodes: list

    """

    def __init__(self, name, nodes):
        CompositeNode.__init__(self, name, nodes)
        if len(nodes) != 2:
            raise ValueError('Compose only operates on two sources.')

    def render(self, context):
        assert isinstance(context, RenderContext)

        feature1 = self._nodes[0].render(context)
        if feature1 is None:
            raise RuntimeError('Render Failed, Node: %s, Context: %r',
                                self._nodes[0].name, context)
        src = feature1.data

        feature2 = self._nodes[1].render(context)
        if feature2 is None:
            raise RuntimeError('Render Failed, Node: %s, Context: %r',
                                self._nodes[1].name, context)
        dst = feature2.data

        if src.mode != dst.mode:
            if src.mode != 'RGBA':
                src = src.convert(mode='RGBA')
            if dst.mode != 'RGBA':
                dst = dst.convert(mode='RGBA')

        pil_image = Image.alpha_composite(dst, src)

        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert(mode='RGBA')

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature
