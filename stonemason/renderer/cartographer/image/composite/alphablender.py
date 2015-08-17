# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

from PIL import Image

from stonemason.renderer.engine.rendernode import CompositeNode
from stonemason.renderer.engine.context import RenderContext

from ..feature import ImageFeature

__all__ = ['AlphaBlender']


class AlphaBlender(CompositeNode):
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

        pil_image = Image.blend(src, dst, self._alpha).convert('RGBA')

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature
