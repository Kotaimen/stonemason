# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/19/15'

import unittest

from stonemason.provider.formatbundle import MapType, InvalidMapType


class TestMapType(unittest.TestCase):
    def test_init(self):
        self.assertEqual(MapType('raster').type, 'raster')
        self.assertEqual(MapType('image').type, 'image')

    def test_init_fail(self):
        self.assertRaises(InvalidMapType, MapType, 'foobar')


if __name__ == '__main__':
    unittest.main()
