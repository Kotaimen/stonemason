# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

import unittest

from stonemason.renderer_ import ImageFeature, RasterFeature, VectorFeature


class TestImageFeature(unittest.TestCase):
    def test_init(self):
        feature = ImageFeature()
        self.assertIsNone(feature.crs)
        self.assertIsNone(feature.bounds)
        self.assertIsNone(feature.size)
        self.assertIsNone(feature.data)
        feature = ImageFeature(
            crs='EPSG:3857',
            bounds=(-180, -85, 180, 85),
            size=(256, 256),
            data=b'data')
        self.assertEqual('EPSG:3857', feature.crs)
        self.assertEqual((-180, -85, 180, 85), feature.bounds)
        self.assertEqual((256, 256), feature.size)
        self.assertEqual(b'data', feature.data)

    def test_repr(self):
        feature = ImageFeature(
            crs='EPSG:3857',
            bounds=(-180, -85, 180, 85),
            size=(256, 256),
            data='data')

        self.assertEqual(
            "ImageFeature(crs='EPSG:3857', bounds=(-180, -85, 180, 85), size=(256, 256))",
            repr(feature))
