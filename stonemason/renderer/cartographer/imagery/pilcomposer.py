# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/6/15'

from ...layerexpr import CompositeLayer
from ...context import RenderContext
from ...feature import ImageFeature

from . import compop


class PILCompositeError(Exception):
    pass


class InvalidCommand(PILCompositeError):
    pass


class PILComposer(CompositeLayer):
    PROTOTYPE = 'pil.composer'

    SUPPORTED_MODES = {
        # Alpha composite
        'clear': compop.comp_op_clear,
        'src': compop.comp_op_src,
        'dst': compop.comp_op_dst,
        'src-in': compop.comp_op_src_in,
        'dst-in': compop.comp_op_dst_in,
        'src-over': compop.comp_op_src_over,
        'dst-over': compop.comp_op_dst_over,
        'src-atop': compop.comp_op_src_atop,
        'dst-atop': compop.comp_op_dst_atop,
        'src-out': compop.comp_op_src_out,
        'dst-out': compop.comp_op_dst_out,
        'xor': compop.comp_op_xor,

        # Mathematical composite
        'multiply': compop.comp_op_multiply,
        'screen': compop.comp_op_screen,
        'overlay': compop.comp_op_overlay,
        'lighten': compop.comp_op_lighten,
        'darken': compop.comp_op_darken,
        'plus': compop.comp_op_plus,
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
            img = l.render(context).data
            img = img.convert('RGBA')

            arr = compop.img2array(img)
            arr = compop.img_as_float(arr)
            arr = compop.premultiply(arr)

            stack.append(arr)

        dst = stack.pop()
        for cmd in self._command:
            src = stack.pop()
            dst = self.SUPPORTED_MODES[cmd](src, dst)

        img = compop.demultiply(dst)
        img = compop.img_as_ubyte(img)
        img = compop.array2img(img, mode='RGBA')

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=img)

        return feature
