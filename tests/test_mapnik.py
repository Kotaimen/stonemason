# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/9/15'

import unittest
import os
import sys

from PIL import Image
from tests import skipUnlessHasMapnik, HAS_MAPNIK, \
    SAMPLE_THEME_DIRECTORY, TEST_DIRECTORY

if HAS_MAPNIK:
    import mapnik


@skipUnlessHasMapnik()
class TestMapnikSetup(unittest.TestCase):
    def test_mapnik_version(self):
        # Requires 2.2.0 or higher, install from PPA
        self.assertGreaterEqual(mapnik.mapnik_version(), 200200)

    def test_manpik_plugins(self):
        pass


@skipUnlessHasMapnik()
class TestMapnikRendering(unittest.TestCase):
    def setUp(self):
        # The sample_world theme uses Dejavu font family which is either
        # distrubuted by mapnik or fonts-dejavu-core package.
        if sys.platform == 'darwin':
            mapnik.register_fonts('/Library/Fonts/')
        elif sys.platform == 'linux2':
            mapnik.register_fonts('/usr/share/fonts')

        theme_root = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_world')
        self.style_sheet = os.path.join(theme_root, 'sample_world.xml')

        self.map = mapnik.Map(512, 512)  # zoom > 1 so admin0 label got rendered
        mapnik.load_map(self.map, self.style_sheet)

    def test_sample_render(self):
        image = mapnik.Image(self.map.width, self.map.height)

        # google maps coverage
        bbox = (-20037508.34, -20037508.34, 20037508.34, 20037508.34)
        self.map.zoom_to_box(mapnik.Box2d(*bbox))
        mapnik.render(self.map, image)

        image_file = os.path.join(TEST_DIRECTORY, 'sample_world.png')
        image.save(image_file, 'png32')

        pil_image = Image.open(image_file)
        self.assertEqual(pil_image.format, 'PNG')

    def test_raw_image(self):
        image = mapnik.Image(self.map.width, self.map.height)
        bbox = (-20037508.34, -20037508.34, 20037508.34, 20037508.34)
        self.map.zoom_to_box(mapnik.Box2d(*bbox))
        mapnik.render(self.map, image)

        raw_data = image.tostring()

        # Image.frombytes() copies image data, Image.frombuffer() donesn't
        pil_image = Image.frombuffer('RGBA',
                                     (self.map.width, self.map.height),
                                     raw_data,
                                     'raw', 'RGBA', 0, 1)
        del image
        self.assertTupleEqual(pil_image.size, (512, 512))


if __name__ == '__main__':
    unittest.main()
