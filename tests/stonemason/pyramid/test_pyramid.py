# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/23/15'

import unittest

from stonemason.pyramid import Pyramid


class TestPyramid(unittest.TestCase):
    def test_init(self):
        pyramid = Pyramid()
        self.assertEqual(pyramid.levels, list(range(0, 23)))
        self.assertEqual(pyramid.stride, 1)
        self.assertTupleEqual(pyramid.geogbounds,
                              (-180, -85.0511, 180, 85.0511))
        self.assertTupleEqual(pyramid.projbounds,
                              (-20037508.34, -20037508.34, 20037508.34,
                               20037508.34))

        self.assertEqual(pyramid.geogcs, 'WGS84')
        self.assertEqual(pyramid.projcs, 'EPSG:3857')

    def test_repr(self):
        pyramid = Pyramid(levels=[4, 5], stride=4)
        self.assertEqual(str(pyramid),
                         "Pyramid(levels=[4, 5], stride=4, projcs='EPSG:3857', "
                         "geogcs='WGS84', "
                         "projbounds=(-20037508.34, -20037508.34, 20037508.34, 20037508.34), "
                         "geogbounds=(-180, -85.0511, 180, 85.0511))")


if __name__ == '__main__':
    unittest.main()
