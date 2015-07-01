# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

import numpy as np
from PIL import Image, ImageMath, ImageChops, ImageOps

from ...layerexpr import ImageryLayer, TransformLayer, CompositeLayer
from ...feature import ImageFeature
from ...context import RenderContext


class PILCartoError(Exception):
    pass


class InvalidCommand(PILCartoError):
    pass


class PILColor(ImageryLayer):
    PROTOTYPE = 'pil.color'

    def __init__(self, name, color='black'):
        ImageryLayer.__init__(self, name)
        self._color = color

    def render(self, context):
        assert isinstance(context, RenderContext)
        im = Image.new("RGB", context.map_size, color=self._color)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=im)
        return feature


class PILInvert(TransformLayer):
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


class PILBlend(CompositeLayer):
    PROTOTYPE = 'pil.blend'

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


def pil_over(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    size = dst.size
    mask = Image.new('1', size, 1)

    im = Image.composite(dst, src, mask)

    return im


def pil_screen(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.screen(dst, src)

    return im


def pil_lighten(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.lighter(dst, src)

    return im


def pil_darken(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.darker(dst, src)

    return im


def pil_add(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.add(dst, src)

    return im


def pil_subtract(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.subtract(dst, src)

    return im


def pil_difference(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.difference(dst, src)

    return im


def pil_multiply(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    im = ImageChops.multiply(dst, src)

    return im


def pil_overlay(dst, src):
    # from agg overlay
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    dst_array = np.array(dst.convert('RGBA'))
    src_array = np.array(src.convert('RGBA'))

    base_mask = np.iinfo(dst_array.dtype).max
    base_shift = base_mask.bit_length()
    cal_type = np.int
    val_type = dst_array.dtype

    sr = src_array[..., 0].astype(cal_type)
    sg = src_array[..., 1].astype(cal_type)
    sb = src_array[..., 2].astype(cal_type)
    sa = src_array[..., 3].astype(cal_type)

    dr = dst_array[..., 0].astype(cal_type)
    dg = dst_array[..., 1].astype(cal_type)
    db = dst_array[..., 2].astype(cal_type)
    da = dst_array[..., 3].astype(cal_type)

    d1a = (base_mask - da).astype(cal_type)
    s1a = (base_mask - sa).astype(cal_type)
    sada = (sa * da).astype(cal_type)

    dr = np.where(
        2 * dr < da,
        2 * sr * dr + sr * d1a + dr * s1a,
        sada - 2 * (da - dr) * (sa - sr) + sr * d1a + dr * s1a + base_mask)
    dr = np.right_shift(dr, base_shift).astype(val_type)

    dg = np.where(
        2 * dg < da,
        2 * sg * dg + sg * d1a + dg * s1a,
        sada - 2 * (da - dg) * (sa - sg) + sg * d1a + dg * s1a + base_mask)
    dg = np.right_shift(dg, base_shift).astype(val_type)

    db = np.where(
        2 * db < da,
        2 * sb * db + sb * d1a + db * s1a,
        sada - 2 * (da - db) * (sa - sb) + sb * d1a + db * s1a + base_mask)
    db = np.right_shift(db, base_shift).astype(val_type)

    da = (sa + da -
          np.right_shift(sa * da + base_mask, base_shift)).astype(val_type)

    result = np.dstack((dr, dg, db, da))

    im = Image.fromarray(result, 'RGBA')
    return im


class PILComposer(CompositeLayer):
    PROTOTYPE = 'pil.composer'

    SUPPORTED_MODES = {
        'over': pil_over,

        # Multiply and Screens
        'screen': pil_screen,
        'multiply': pil_multiply,
        'overlay': pil_overlay,

        # Simple arithmetic blend modes
        'lighten': pil_lighten,
        'darken': pil_darken,
        'add': pil_add,
        'subtract': pil_subtract,
        'difference': pil_difference,
    }

    def __init__(self, name, layers, command=None):
        CompositeLayer.__init__(self, name, layers)
        assert isinstance(command, list) and len(command) == len(layers) - 1
        if not isinstance(command, list):
            raise InvalidCommand('Compose command should be a list.')

        if len(command) != len(layers) - 1:
            raise InvalidCommand('Compose command and source layers not match.')

        for cmd in command:
            if cmd not in self.SUPPORTED_MODES:
                raise InvalidCommand('Unsupported compose command %s' % cmd)

        self._command = command

    def render(self, context):
        assert isinstance(context, RenderContext)

        stack = []
        for l in self._layers:
            stack.append(l.render(context).data)

        dst = stack.pop()
        for cmd in self._command:
            src = stack.pop()
            im = self.SUPPORTED_MODES[cmd](dst, src)

            dst = im

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=dst)

        return feature
