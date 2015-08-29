# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.terminal.color
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An input image with arbitrary single color.
"""

__author__ = 'ray'
__date__ = '8/7/15'

from PIL import Image, ImageColor

from stonemason.renderer.engine.rendernode import TermNode
from stonemason.renderer.engine.context import RenderContext

from ..feature import ImageFeature

__all__ = ['Color']


class Color(TermNode):
    """Color Render Node

    A `Color` render node renders a image feature of a single color. It could
    be represented in the render expression as following:

    :param name: a string literal that identifies the node
    :type name: str

    :param color: a color string, see `Color Names`_ for detail.
    :type str: str

    .. _Color Names: http://pillow.readthedocs.org/en/latest/reference/ImageColor.html#color-names

    """
    def __init__(self, name, color='#000'):
        TermNode.__init__(self, name)
        self._color = ImageColor.getrgb(color)

    def render(self, context):
        """Render a image feature.

        :param context: requirements and conditions for feature rendering.
        :type context: :class:`~stonemason.renderer.engine.RenderContext`

        :return: a image feature.
        :rtype: :class:`~stonemason.renderer.cartographer.image.ImageFeature`

        """
        assert isinstance(context, RenderContext)

        pil_image = Image.new('RGBA', context.map_size, color=self._color)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature
