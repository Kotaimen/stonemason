# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.composite.alphablender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of composite render node that performs alpha blending.
"""
__author__ = 'ray'
__date__ = '8/7/15'

from PIL import Image

from stonemason.renderer.engine.rendernode import CompositeNode
from stonemason.renderer.engine.context import RenderContext

from ..feature import ImageFeature

__all__ = ['AlphaBlender']


class AlphaBlender(CompositeNode):
    """Alpha Blender

    `AlphaBlender` is a composite node that performs alpha blending on
    two source nodes.

    .. math::

        \\begin{align}
        src1 & = nodes[0] \\\\
        src2 & = nodes[1] \\\\
        out & = src1 \\times (1.0 - alpha) + src2 \\times alpha
        \\end{align}

    :param name: a string literal that identifies the node
    :type name: str

    :param nodes: a list of two source render nodes.
    :type nodes: list

    :param alpha: alpha value for alpha blending, ranging from ``0`` to ``1.0``.
        default value is ``0.5``.
    :type alpha: float

    """

    def __init__(self, name, nodes, alpha=0.5):
        CompositeNode.__init__(self, name, nodes)
        if len(nodes) != 2:
            raise ValueError('Blend only operates on two sources.')
        if alpha > 1 or alpha < 0:
            raise ValueError('Invalid alpha value %f' % alpha)
        self._alpha = alpha

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._nodes[0].render(context).data
        dst = self._nodes[1].render(context).data

        if src.mode != dst.mode:
            if src.mode != 'RGBA':
                src = src.convert(mode='RGBA')
            if dst.mode != 'RGBA':
                dst = dst.convert(mode='RGBA')

        pil_image = Image.blend(src, dst, self._alpha)

        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert(mode='RGBA')

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature
