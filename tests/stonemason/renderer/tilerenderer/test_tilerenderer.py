# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/25/15'

import unittest

from stonemason.pyramid import Pyramid, MetaTileIndex
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer.tilerenderer import ImageMetaTileRenderer
from stonemason.renderer.tilerenderer import RendererExprParser

from tests import skipUnlessHasGDAL


@skipUnlessHasGDAL()
class TestImageMetaTileRenderer(unittest.TestCase):
    def test_build_base_renderer(self):
        d = {
            'root': {
                'type': 'dummy',
            }
        }

        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        renderer = RendererExprParser(pyramid).parse_from_dict(
            d, 'root').interpret()
        tilerenderer = ImageMetaTileRenderer(pyramid, bundle, renderer)

        meta_index = MetaTileIndex(1, 0, 0, 2)
        self.assertIsNone(tilerenderer.render_metatile(meta_index))

    def test_build_transform_renderer(self):
        d = {
            'layer1': {
                'type': 'dummy'
            },
            'root': {
                'type': 'dummy',
                'source': 'layer1'
            }
        }

        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        renderer = RendererExprParser(pyramid).parse_from_dict(
            d, 'root').interpret()
        tilerenderer = ImageMetaTileRenderer(pyramid, bundle, renderer)

        meta_index = MetaTileIndex(1, 0, 0, 2)
        self.assertIsNone(tilerenderer.render_metatile(meta_index))

    def test_build_composite_renderer(self):
        d = {
            'layer1': {
                'type': 'dummy'
            },
            'layer2': {
                'type': 'dummy'
            },
            'root': {
                'type': 'dummy',
                'sources': ['layer1', 'layer2']
            }
        }

        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        renderer = RendererExprParser(pyramid).parse_from_dict(
            d, 'root').interpret()
        tilerenderer = ImageMetaTileRenderer(pyramid, bundle, renderer)

        meta_index = MetaTileIndex(1, 0, 0, 2)
        self.assertIsNone(tilerenderer.render_metatile(meta_index))
