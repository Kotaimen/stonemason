# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import os

from PIL import Image

from stonemason.renderer.cartographer.imagery import Mapnik_, MapnikComposer
from stonemason.renderer.context import RenderContext
from stonemason.pyramid import Pyramid, MetaTileIndex
from stonemason.pyramid.geo import TileMapSystem

from tests import SAMPLE_THEME_DIRECTORY, DATA_DIRECTORY, TEST_DIRECTORY
from tests import skipUnlessHasMapnik, ImageTestCase


@skipUnlessHasMapnik()
class TestMapnikLayer(ImageTestCase):
    def setUp(self):
        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        style_sheet = os.path.join(theme_root, 'sample_world.xml')

        self._layer = Mapnik_('mapnik', style_sheet=style_sheet)

    def test_image(self):
        context = RenderContext(
            map_proj='+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs',
            map_bbox=(-10037508.34, -10037508.34, 10037508.34, 10037508.34),
            map_size=(512, 512),
        )

        image = self._layer.render(context).data

        test_data_root = os.path.join(DATA_DIRECTORY, 'cartographer')
        test_file = os.path.join(test_data_root, 'mapnik_sample_world.png')
        # image.save(test_file, 'png')

        expected = Image.open(test_file)
        self.assertImageEqual(expected, image)

    def test_render_with_tms1(self):
        pyramid = Pyramid(projcs='EPSG:2964',
                          geogcs=None,
                          geogbounds=(-180, 30, -70, 70),
                          projbounds=None)

        tms = TileMapSystem(pyramid)
        index = MetaTileIndex(4, 0, 0, 16)
        bbox = tms.calc_tile_envelope(index)

        context = RenderContext(map_proj=tms.pyramid.projcs,
                                map_bbox=bbox,
                                map_size=(512, 512))

        test_file = os.path.join(TEST_DIRECTORY, 'EPSG_2964.png')

        image = self._layer.render(context).data

        image.save(test_file, 'png')

    def test_render_with_tms2(self):
        pyramid = Pyramid(projcs='EPSG:102010',
                          # North America Equidistant Conic
                          geogcs='NAD83',
                          geogbounds=(-160, 20, -55, 75),
                          projbounds=(-6200000, -360000, 3740000, 500000 ))

        tms = TileMapSystem(pyramid)
        index = MetaTileIndex(4, 0, 0, 16)
        bbox = tms.calc_tile_envelope(index)

        context1 = RenderContext(map_proj=tms.pyramid.projcs,
                                 map_bbox=bbox,
                                 map_size=(1024, 1024),
                                 scale_factor=1)
        context2 = RenderContext(map_proj=tms.pyramid.projcs,
                                 map_bbox=bbox,
                                 map_size=(1024, 1024),
                                 scale_factor=2)

        image1 = self._layer.render(context1).data
        image2 = self._layer.render(context2).data

        self.assertImageNotEqual(image1, image2)

        output1 = os.path.join(TEST_DIRECTORY, 'EPSG_102010@1x.png')
        output2 = os.path.join(TEST_DIRECTORY, 'EPSG_102010@2x.png')

        image1.save(output1, 'png')
        image1.save(output2, 'png')


@skipUnlessHasMapnik()
class TestMapnikComposer(ImageTestCase):
    def setUp(self):
        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        self.style_sheet = os.path.join(theme_root, 'sample_world.xml')

    def test_compose_with_two(self):
        layer = MapnikComposer(
            'mapnik.composer',
            style_sheets=[self.style_sheet, self.style_sheet],
            commands=[('multiply', {})]
        )

        context = RenderContext(
            map_proj='+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs',
            map_bbox=(-10037508.34, -10037508.34, 10037508.34, 10037508.34),
            map_size=(512, 512),

        )

        image = layer.render(context).data

        # image.show()

        test_data_root = os.path.join(DATA_DIRECTORY, 'cartographer')
        test_file = os.path.join(test_data_root, 'mapnik_compose_two.png')
        # image.save(test_file, 'png')

        expected = Image.open(test_file)
        self.assertImageEqual(expected, image)


    def test_compose_with_three(self):
        layer = MapnikComposer(
            'mapnik.composer',
            style_sheets=[
                self.style_sheet,
                self.style_sheet,
                self.style_sheet,
            ],
            commands=[('multiply', {}), ('multiply', {}), ])

        context = RenderContext(
            map_proj='+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs',
            map_bbox=(-10037508.34, -10037508.34, 10037508.34, 10037508.34),
            map_size=(512, 512),
        )

        image = layer.render(context).data

        # image.show()

        test_data_root = os.path.join(DATA_DIRECTORY, 'cartographer')
        test_file = os.path.join(test_data_root, 'mapnik_compose_three.png')
        # image.save(test_file, 'png')

        expected = Image.open(test_file)
        self.assertImageEqual(expected, image)
