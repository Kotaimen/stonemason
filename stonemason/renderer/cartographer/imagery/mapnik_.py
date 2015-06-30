# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import os
import mapnik

from PIL import Image

from ...layerexpr import ImageryLayer
from ...feature import ImageFeature
from ...context import RenderContext


class MapnikCartoError(Exception):
    pass


class InvalidComposeMode(MapnikCartoError):
    pass


class InvalidCommandNumber(MapnikCartoError):
    pass


class Mapnik_(ImageryLayer):
    PROTOTYPE = 'mapnik'

    def __init__(self, name,
                 style_sheet='map.xml',
                 buffer_size=0,
                 base_path=None,
                 default_scale=None):
        ImageryLayer.__init__(self, name)
        assert isinstance(buffer_size, int)

        # check theme path
        self._style_sheet = style_sheet
        self._default_scale = default_scale
        self._map = mapnik.Map(32, 32)

        filename = self._style_sheet.encode('utf-8')
        filename = os.path.abspath(filename)
        if base_path is None:
            base_path = os.path.dirname(filename)

        mapnik.load_map(self._map, filename, True, base_path)
        self._map.buffer_size = buffer_size

    def render(self, context):
        assert isinstance(context, RenderContext)

        if self._default_scale is None:
            scale = context.scale_factor
        else:
            scale = self._default_scale

        projcs = context.map_proj
        proj = mapnik.Projection(projcs)

        bbox = mapnik.Box2d(*context.map_bbox)
        map_width, map_height = context.map_size

        self._map.srs = proj.params()
        self._map.resize(map_width, map_height)
        self._map.zoom_to_box(bbox)

        image = mapnik.Image(map_width, map_height)
        mapnik.render(self._map, image, scale)

        raw_data = image.tostring()

        pil_image = Image.frombuffer(
            'RGBA', (map_width, map_height), raw_data, 'raw', 'RGBA', 0, 1)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image)

        return feature


class MapnikComposer(ImageryLayer):
    PROTOTYPE = 'mapnik.composer'

    def __init__(self, name, style_sheets, commands,
                 buffer_size=0,
                 base_path=None,
                 default_scale=None):
        ImageryLayer.__init__(self, name)
        assert isinstance(style_sheets, list)
        assert isinstance(commands, list)
        
        if len(commands) != len(style_sheets) - 1:
            raise InvalidCommandNumber(
                'len(commands) should be len(style_sheets) - 1')

        self._default_scale = default_scale
        self._commands = commands

        self._maps = list()
        for style_sheet in style_sheets:
            map = mapnik.Map(32, 32)

            filename = os.path.abspath(style_sheet)
            if base_path is None:
                base_path = os.path.dirname(filename)

            mapnik.load_map(map, filename, True, base_path)
            map.buffer_size = buffer_size
            self._maps.append(map)

    def render(self, context):
        assert isinstance(context, RenderContext)

        base = self.render_mapnik_image(self._maps[0], context)
        base.premultiply()

        for map, cmd in zip(self._maps[1:], self._commands):
            img = self.render_mapnik_image(map, context)
            img.premultiply()

            mode, opacity = cmd
            try:
                op = mapnik.CompositeOp.names[mode]
            except KeyError:
                raise InvalidComposeMode(mode)

            base.composite(img, op, opacity)

        base.demultiply()

        raw_data = base.tostring()

        pil_image = Image.frombuffer(
            'RGBA', (base.width(), base.height()), raw_data, 'raw', 'RGBA', 0,
            1)

        feature = ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=pil_image)

        return feature

    def render_mapnik_image(self, map, context):
        assert isinstance(context, RenderContext)

        if self._default_scale is None:
            scale = context.scale_factor
        else:
            scale = self._default_scale

        projcs = context.map_proj
        proj = mapnik.Projection(projcs)

        bbox = mapnik.Box2d(*context.map_bbox)
        map_width, map_height = context.map_size

        map.srs = proj.params()
        map.resize(map_width, map_height)
        map.zoom_to_box(bbox)

        image = mapnik.Image(map_width, map_height)
        mapnik.render(map, image, scale)

        return image
