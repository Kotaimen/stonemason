# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.feature
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of image render result.
"""

__author__ = 'ray'
__date__ = '8/17/15'

from stonemason.renderer.engine.feature import Feature


class ImageFeature(Feature):
    """Image Feature

    A image feature is the rendering result of a image render node. It is a geo
    referenced image object.

    :param crs: The coordinate reference system of the feature.
    :type crs: str
    :param bounds: a tuple of ``(left, bottom, right, top)`` that represents
        boundary of the feature.
    :type bounds: tuple
    :param size: a tuple of ``(width, height)`` that represents the pixel size
        of the area of the feature.
    :type size: tuple
    :param data: feature data.
    :type data: :class:`PIL.Image`

    """
    pass
