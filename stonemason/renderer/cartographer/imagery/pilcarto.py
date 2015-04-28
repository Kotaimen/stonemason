# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/20/15'

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


# Just for test
def pil_overlay(dst, src):
    assert isinstance(dst, Image.Image)
    assert isinstance(src, Image.Image)

    POSITION = (253, 253)

    print ('dst:', dst.getpixel(POSITION))
    print ('src:', src.getpixel(POSITION))

    dst_bands = dst.split()
    src_bands = src.split()
    mask = dst.point(lambda i: i <= 127 and 255 or 0)

    print ('mask:', mask.getpixel(POSITION))

    def _multiply(d, s):
        im = ImageMath.eval(
            '2 * float(a) * float(b) / 255.0 + 0.5', a=d, b=s).convert('L')
        return im

    def _screen(d, s):
        im = ImageMath.eval(
            '255 - (2 * (255.0 - float(a)) * (255.0 - float(b)) / 255.0) + 0.5',
            a=d, b=s).convert('L')
        return im

    def _composite(d, s, m):
        im = ImageMath.eval(
            'm * a / 255 + (255 - m) * b / 255', m=m, a=d, b=s).convert('L')
        return im

    branch1 = Image.merge('RGBA', map(_multiply, dst_bands, src_bands))
    print ('b1:', branch1.getpixel(POSITION))

    branch2 = Image.merge('RGBA', map(_screen, dst_bands, src_bands))
    print ('b2:', branch2.getpixel(POSITION))

    result = Image.merge('RGBA',
                         map(_composite, branch1.split(), branch2.split(),
                             mask.split()))
    # result = Image.composite(branch1, branch2, mask)

    print ('result:', result.getpixel(POSITION))
    return result


class PILComposer(CompositeLayer):
    PROTOTYPE = 'pil.compose'

    SUPPORTED_MODES = {
        'over': pil_over,

        # Multiply and Screens
        'screen': pil_screen,
        'multiply': pil_multiply,

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
