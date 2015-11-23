# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/23/15'

import os
import unittest
from osgeo import gdal, gdalconst, gdalnumeric
from stonemason.storage.featurestorage.raster.serializer import \
    RasterFeatureSerializer
from tests import DATA_DIRECTORY


class TestRasterFeatureSerializer(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(DATA_DIRECTORY, 'raster', 'fujisan_5m.tif')

    def test_load(self):
        serializer = RasterFeatureSerializer()
        with open(self.filename, 'rb') as fp:
            blob = fp.read()
            obj = serializer.load('test_index', blob=blob, metadata={})

        expected = gdal.Open(self.filename, gdalconst.GA_ReadOnly)
        self.assertIsInstance(obj, gdal.Dataset)
        self.assertEqual(expected.RasterCount, obj.RasterCount)
        self.assertEqual(expected.RasterXSize, obj.RasterXSize)
        self.assertEqual(expected.GetProjectionRef(), obj.GetProjectionRef())
        self.assertTrue(gdalnumeric.array_equal(
            expected.ReadAsArray(), obj.ReadAsArray()))

    def test_save(self):
        serializer = RasterFeatureSerializer()

        obj = gdal.Open(self.filename, gdalconst.GA_ReadOnly)
        print(obj.RasterCount)
        print(obj.RasterXSize)
        print(obj.RasterYSize)

        band = obj.GetRasterBand(1)
        print(gdal.GetDataTypeName(band.DataType))


        blob, metadata = serializer.save('test_index', obj)

        self.assertIsNotNone(blob)
        self.assertDictEqual({}, metadata)


    def test_load_save(self):
        serializer = RasterFeatureSerializer()

        expected = gdal.Open(self.filename, gdalconst.GA_ReadOnly)

        blob, metadata = serializer.save('test_index', expected)
        obj = serializer.load('test_index', blob, metadata)

        self.assertIsInstance(obj, gdal.Dataset)
        self.assertEqual(expected.RasterCount, obj.RasterCount)
        self.assertEqual(expected.RasterXSize, obj.RasterXSize)
        self.assertEqual(expected.GetProjectionRef(), obj.GetProjectionRef())
        self.assertTrue(gdalnumeric.array_equal(
            expected.ReadAsArray(), obj.ReadAsArray()))
