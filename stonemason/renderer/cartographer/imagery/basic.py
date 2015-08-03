# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/6/15'

import numpy as np
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


class _FilterLayer(TransformLayer):
    def __init__(self, name, layer, image_filter):
        TransformLayer.__init__(self, name, layer)
        self._filter = image_filter

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._layer.render(context).data

        pil_image = src.filter(self._filter)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature


class MedianPILFilter(_FilterLayer):
    PROTOTYPE = 'basic.filter.MedianFilter'

    def __init__(self, name, layer, size=3):
        image_filter = ImageFilter.MedianFilter(size)
        _FilterLayer.__init__(self, name, layer, image_filter)


class MinPILFilter(_FilterLayer):
    PROTOTYPE = 'basic.filter.MinFilter'

    def __init__(self, name, layer, size=3):
        image_filter = ImageFilter.MinFilter(size)
        _FilterLayer.__init__(self, name, layer, image_filter)


class MaxPILFilter(_FilterLayer):
    PROTOTYPE = 'basic.filter.MaxFilter'

    def __init__(self, name, layer, size=3):
        image_filter = ImageFilter.MaxFilter(size)
        _FilterLayer.__init__(self, name, layer, image_filter)


class GaussianBlurPILFilter(_FilterLayer):
    PROTOTYPE = 'filter.GaussianBlur'

    def __init__(self, name, layer, radius=2):
        image_filter = ImageFilter.GaussianBlur(radius)
        _FilterLayer.__init__(self, name, layer, image_filter)


class UnsharpMaskPILFilter(_FilterLayer):
    PROTOTYPE = 'basic.filter.UnsharpMask'

    def __init__(self, name, layer, radius=2, percent=150, threshold=3):
        image_filter = ImageFilter.UnsharpMask(radius, percent, threshold)
        _FilterLayer.__init__(self, name, layer, image_filter)


class GammaAdjustment(TransformLayer):
    PROTOTYPE = 'basic.exposure.gamma'

    def __init__(self, name, layer, gamma=1, gain=1):
        TransformLayer.__init__(self, name, layer)
        if gamma < 0:
            raise ValueError("Gamma should be a non-negative real number.")

        self._gamma = gamma
        self._gain = gain

    def render(self, context):
        assert isinstance(context, RenderContext)

        src = self._layer.render(context).data

        array = np.array(src)

        dtype = array.dtype.type
        dtype_limits = np.iinfo(dtype)

        scale = float(dtype_limits.max - dtype_limits.min)

        out = ((array / scale) ** self._gamma) * scale * self._gain
        out = dtype(out)

        pil_image = Image.fromarray(out, mode='RGBA')

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

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
