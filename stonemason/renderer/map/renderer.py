# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.map.renderer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the interface of different kinds of renderers.

"""

__author__ = 'ray'
__date__ = '3/19/15'


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

