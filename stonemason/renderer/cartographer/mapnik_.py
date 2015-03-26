# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/11/15'

import mapnik
from PIL import Image

from ..map import BaseLayer, ImageMapRenderer, RenderContext


class MapnikMapRenderer(BaseLayer, ImageMapRenderer):
    """Mapnik Layer

    Mapnik is a Free Toolkit for developing mapping applications.
    It is written in modern C++ and has Python bindings that support
    fast-paced agile development.

    The `MapnikLayer` outputs image data on the projection plane defined in the
    `MapContext` acting as a leaf layer in the layer hierarchy.

    :param name: A literal string that identifies the layer.
    :type name: str

    :param style_sheet: A literal string that indicates the file path of the
                        style sheet.
    :type style_sheet: str

    :param scale_factor: A fractional value that is used as a multiplier
                         throughout the rendering pipeline. Using `scale_factor`
                         to scale up or down rendering sizes such as line width,
                         line dash-array separation, svg and png icon size,
                         font size, halo size, glyph spacing, and many more.
    :type scale_factor: float

    :param buffer_size: A positive integer value used indicate the extra
                        area to render to avoid cutting symbols in target map.
    :type buffer_size: int

    """
    def __init__(self, name,
                 style_sheet='map.xml',
                 scale_factor=1.0,
                 buffer_size=0):
        BaseLayer.__init__(self, name)
        assert isinstance(scale_factor, float)
        assert isinstance(buffer_size, int)

        # check theme path
        self._style_sheet = style_sheet
        self._scale_factor = scale_factor

        self._map = mapnik.Map(32, 32)
        mapnik.load_map(self._map, self._style_sheet)
        self._map.buffer_size = buffer_size

    def image(self, context):
        assert isinstance(context, RenderContext)

        projcs = context.pyramid.projcs
        proj = mapnik.Projection(projcs)

        bbox = mapnik.Box2d(*context.target_bbox)
        map_width, map_height = context.target_size

        self._map.srs = proj.params()
        self._map.resize(map_width, map_height)
        self._map.zoom_to_box(bbox)

        image = mapnik.Image(map_width, map_height)
        mapnik.render(self._map, image, self._scale_factor)

        raw_data = image.tostring()

        pil_image = Image.frombuffer(
            'RGBA', (map_width, map_height), raw_data, 'raw', 'RGBA', 0, 1)

        return pil_image
