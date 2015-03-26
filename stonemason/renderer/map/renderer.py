# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.map.renderer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the interface of different kinds of renderers.

"""

__author__ = 'ray'
__date__ = '3/19/15'

from collections import namedtuple


_RenderContext = namedtuple(
    'RenderContext',
    'pyramid target_bbox target_size')


class RenderContext(_RenderContext):
    """

    :param pyramid: The target space reference system.

    :param target_bbox: The target render area.

    :param target_size: The pixel size of the target bounding box.

    :param target_scale: The target_scale indicates the ratio between map
                         distance and ground distance.

    :param target_resolution: The target_resolution indicates the distance on
                              the ground that represented by a single pixel.
                              For example, ``78271.5170`` meters/pixel.

    """

    def __new__(cls, pyramid=None, target_bbox=None, target_size=None):
        return _RenderContext.__new__(
            cls, pyramid=pyramid,
            target_bbox=target_bbox,
            target_size=target_size)


class ImageMapRenderer(object):
    def image(self, context):
        """Rendering an image representation of a map layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.RenderContext`

        :return: A PIL image that represents the data of area defined in map
                 context.
        :rtype: :class:`PIL.Image`

        """
        raise NotImplementedError


class RasterMapRenderer(object):
    def raster(self, context):
        """Rendering a Raster representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.RenderContext`

        :return: A raster object that represents the data of area defined in map
                 context.
        :rtype: :class:`gdal.Dataset`

        """
        raise NotImplementedError


class VectorMapRenderer(object):
    def vector(self, context):
        """Rendering a vector representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.RenderContext`

        :return: A GeoJson that represents the data of area defined in map
                 context.
        :rtype: str

        """
        raise NotImplementedError

