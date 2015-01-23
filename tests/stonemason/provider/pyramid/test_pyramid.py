# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/23/15'

import unittest

from stonemason.provider.pyramid import Pyramid


class TestPyramid(unittest.TestCase):
    def test_init(self):
        pyramid = Pyramid()
        self.assertEqual(pyramid.levels, list(range(0, 23)))
        self.assertEqual(pyramid.stride, 1)
        self.assertListEqual(list(pyramid.boundary),
                             [-180, -85.0511, 180, 85.0511])
        self.assertEqual(pyramid.crs, 'EPSG:4326')
        self.assertEqual(pyramid.proj, 'EPSG:3857')

    def test_repr(self):
        pyramid = Pyramid(levels=[4,5], stride=4)
        self.assertEqual(str(pyramid),
                         '''Pyramid(levels=[4, 5], stride=4, crs='EPSG:4326', proj='EPSG:3857', boundary=(-180, -85.0511, 180, 85.0511))''')



if __name__ == '__main__':
    unittest.main()
