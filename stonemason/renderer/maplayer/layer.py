# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.maplayer.layer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme and relative theme elements.

"""

__author__ = 'ray'
__date__ = '3/10/15'


class MapLayer(object):
    """Map Layer Interface

    A `Layer` is a single map unit that represents objects designating a common
    source. A normal map usually consists of a tree of layers that represents
    the hierarchy of a map.

    Three different map type could be represented by a layer, image, vector, and
    raster. And primitive layers could be transformed, composed by intermediate
    layers or directly accessed.

    :param name: A string literal that identifies a layer.
    :type name: str

    """

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """Name of layer"""
        return self._name

    def image(self, context):
        """Rendering an image representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A PIL image that represents the data of area defined in map
                 context.
        :rtype: :class:`PIL.Image`

        """
        raise NotImplementedError

    def vector(self, context):
        """Rendering a vector representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A GeoJson that represents the data of area defined in map
                 context.
        :rtype: str

        """
        raise NotImplementedError

    def raster(self, context):
        """Rendering a Raster representation of a layer

        :param context: Context.
        :type context: :class:`stonemason.renderer.maplayer.MapContext`

        :return: A raster object that represents the data of area defined in map
                 context.
        :rtype: :class:`gdal.Dataset`

        """
        raise NotImplementedError

    def __repr__(self):
        return '%s()' % (self.__class__.__name__)


class BaseLayer(MapLayer):
    """Primitive Layer

    A `BaseLayer` acts as a leaf layer of a Map. It takes a `RenderContext`
    and return the supported representation of its objects.
    """
    pass


class TransformLayer(MapLayer):
    """Transform Layer

    A `TransformLayer` accepts a `Layer` object and transform its representation
    from one into another.

    :param name: A string literal that identifies a layer.
    :type name: str

    :param layer: A map layer.
    :type layer: :class:`stonemason.renderer.maplayer.MapLayer`

    """

    def __init__(self, name, layer):
        MapLayer.__init__(self, name)
        self._layer = layer

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._layer)


class CompositeLayer(MapLayer):
    """Composite Layer

    A `CompositeLayer` accepts a list of map layers and compose them into a
    single one.

    :param name: A string literal that identifies a layer.
    :type name: str

    :param layer: A list of map layer.
    :type layers: list

    """

    def __init__(self, name, *layers):
        MapLayer.__init__(self, name)
        self._layers = layers

    def __repr__(self):
        layer_reprs = ', '.join(repr(l) for l in self._layers)
        return '%s(%r)' % (self.__class__.__name__, layer_reprs)






