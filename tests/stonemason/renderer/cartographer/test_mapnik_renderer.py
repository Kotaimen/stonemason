# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/20/15'

import os

from tests import SAMPLE_THEME_DIRECTORY, DATA_DIRECTORY, TEST_DIRECTORY
from tests import skipUnlessHasMapnik, HAS_MAPNIK, ImageTestCase

if HAS_MAPNIK:
    from PIL import Image
    from stonemason.renderer.cartographer import MapnikRenderer
    from stonemason.renderer.map import RenderContext
    from stonemason.pyramid import Pyramid, MetaTileIndex
    from stonemason.pyramid.geo import TileMapSystem


@skipUnlessHasMapnik()
class TestMapnikLayer(ImageTestCase):
    def setUp(self):
        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        style_sheet = os.path.join(theme_root, 'sample_world.xml')

        self._layer = MapnikRenderer('mapnik', style_sheet=style_sheet)

    def test_image(self):
        pyramid = Pyramid(projcs='+init=EPSG:3857')

        context = RenderContext(
            pyramid=pyramid,
            target_bbox=(-10037508.34, -10037508.34, 10037508.34, 10037508.34),
            target_size=(512, 512),
        )

        image = self._layer.image(context)

        test_data_root = os.path.join(DATA_DIRECTORY, 'cartographer')
        test_file = os.path.join(test_data_root, 'mapnik_sample_world.png')
        # image.save(test_file, 'png')

        expected = Image.open(test_file)
        self.assertImageEqual(expected, image)

    def test_render_with_tms(self):
        pyramid = Pyramid(projcs='EPSG:2964',
                          geogcs=None,
                          geogbounds=(-180, 30, -70, 70),
                          projbounds=None)
        tms = TileMapSystem(pyramid)
        index = MetaTileIndex(4, 0, 0, 16)
        bbox = tms.calc_tile_envelope(index)
        context = RenderContext(pyramid=tms.pyramid,
                                target_bbox=bbox,
                                target_size=(512, 512))

        test_file = os.path.join(TEST_DIRECTORY, 'alaska.png')

        image = self._layer.image(context)

        image.save(test_file, 'png')