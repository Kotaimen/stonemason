# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

from PIL import Image, ImageOps, ImageChops

from ...layerexpr import ImageryLayer, TransformLayer, CompositeLayer
from ...feature import ImageFeature
from ...context import RenderContext


class Black(ImageryLayer):
    PROTOTYPE = 'pil.black'

    def __init__(self, name):
        ImageryLayer.__init__(self, name)

    def render(self, context):
        assert isinstance(context, RenderContext)
        im = Image.new("RGB", context.map_size, "black")

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=im)
        return feature


class Invert(TransformLayer):
    PROTOTYPE = 'pil.invert'

    def render(self, context):
        assert isinstance(context, RenderContext)
        source = self._layer.render(context)

        if source.data.mode == 'RGBA':
            r, g, b, a = source.data.split()

            def invert(image):
                return image.point(lambda p: 255 - p)

            r, g, b = map(invert, (r, g, b))

            inv = Image.merge(source.data.mode, (r, g, b, a))
        else:
            inv = ImageChops.invert(source.data)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=inv)
        return feature


class AlphaBlend(CompositeLayer):
    PROTOTYPE = 'pil.blend.alpha'

    def __init__(self, name, layers, alpha=0.5):
        CompositeLayer.__init__(self, name, layers)
        self._alpha = alpha

    def render(self, context):
        assert isinstance(context, RenderContext)
        source = self._layers[0].render(context)
        target = self._layers[1].render(context)
        result = ImageChops.blend(source.data, target.data, self._alpha)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=result)

        return feature


