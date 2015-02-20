# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/19/15'

import unittest

from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle, \
    MapWriter, NoMatchingMapWriter


class TestFormatBundle(unittest.TestCase):
    def test_init(self):
        bundle = FormatBundle(MapType('image'), TileFormat('JPEG'))
        self.assertIsInstance(bundle.map_type, MapType)
        self.assertIsInstance(bundle.tile_format, TileFormat)
        self.assertIsInstance(bundle.writer, MapWriter)

    def test_repr(self):
        self.assertEqual(
            str(FormatBundle(MapType('image'), TileFormat('JPEG'))),
            'FormatBundle(MapType(image), TileFormat(JPEG|image/jpeg|.jpg))')

    def test_writer_fail(self):
        self.assertRaises(NoMatchingMapWriter, FormatBundle,
                          MapType('feature'),
                          TileFormat('JPEG'))


if __name__ == '__main__':
    unittest.main()
