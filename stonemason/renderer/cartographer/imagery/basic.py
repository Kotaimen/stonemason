# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/6/15'

from PIL import Image, ImageColor, ImageFilter

from ...layerexpr import ImageryLayer, TransformLayer, CompositeLayer
from ...feature import ImageFeature
from ...context import RenderContext


class Color(ImageryLayer):
    PROTOTYPE = 'basic.color'

    def __init__(self, name, color='#000'):
        ImageryLayer.__init__(self, name)
        self._color = ImageColor.getrgb(color)

    def render(self, context):
        assert isinstance(context, RenderContext)

        pil_image = Image.new('RGBA', context.map_size, color=self._color)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature


_BUILTIN_FILTERS = dict(
    (i.__name__.lower(), i) for i in ImageFilter.BuiltinFilter.__subclasses__())


class Filter(TransformLayer):
    PROTOTYPE = 'basic.filter'

    def __init__(self, name, layer, filter_name):
        TransformLayer.__init__(self, name, layer)

        filter_name = filter_name.lower()
        if filter_name not in _BUILTIN_FILTERS:
            raise ValueError(
                'Unknown filter name %s, builtin filters include %s' % filter_name,
                _BUILTIN_FILTERS.keys())

        self._filter = _BUILTIN_FILTERS[filter_name]

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._layer.render(context).data

        pil_image = src.filter(self._filter)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature


class Blend(CompositeLayer):
    PROTOTYPE = 'basic.blend'

    def __init__(self, name, layers, alpha=0.5):
        CompositeLayer.__init__(self, name, layers)
        if len(layers) != 2:
            raise ValueError('Blend only operates on two sources.')
        if alpha > 1 or alpha < 0:
            raise ValueError('Invalid alpha value %f' % alpha)
        self._alpha = alpha

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._layers[0].render(context).data
        dst = self._layers[1].render(context).data

        pil_image = Image.blend(src, dst, self._alpha).convert('RGBA')

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image
        )

        return feature
