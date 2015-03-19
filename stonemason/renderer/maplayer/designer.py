# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/19/15'


class ImageDesigner(object):
    def image(self, context):
        """Rendering an image representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A PIL image that represents the data of area defined in map
                 context.
        :rtype: :class:`PIL.Image`

        """
        raise NotImplementedError


class RasterDesigner(object):
    def raster(self, context):
        """Rendering a Raster representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A raster object that represents the data of area defined in map
                 context.
        :rtype: :class:`gdal.Dataset`

        """
        raise NotImplementedError


class VectorDesigner(object):
    def vector(self, context):
        """Rendering a vector representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A GeoJson that represents the data of area defined in map
                 context.
        :rtype: str

        """
        raise NotImplementedError