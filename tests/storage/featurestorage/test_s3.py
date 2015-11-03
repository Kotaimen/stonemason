# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import tempfile
import unittest
import moto
import boto3

from osgeo import osr, gdal, ogr, gdalconst

from stonemason.storage.featurestorage import S3RasterFeatureStorage

from tests import DATA_DIRECTORY

TEST_BUCKET_NAME = 'rasterstorage'


def create_dummy_index(filename, raster_features):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    source = driver.CreateDataSource(filename)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    layer = source.CreateLayer('index', srs=srs, geom_type=ogr.wkbPolygon)
    location_field = ogr.FieldDefn('location', ogr.OFTString)
    layer.CreateField(location_field)

    for raster_key, raster_filename in raster_features:
        raster = gdal.OpenShared(raster_filename, gdalconst.GA_ReadOnly)
        transform = raster.GetGeoTransform()
        origin = transform[0], transform[3]
        resolution = transform[1], -transform[5]
        size = raster.RasterXSize, raster.RasterYSize
        minx, miny = origin[0], origin[1] - resolution[1] * size[1]
        maxx, maxy = origin[0] + resolution[0] * size[0], origin[1]

        index_record = ogr.Feature(layer.GetLayerDefn())
        index_record.SetField('location', raster_key)

        # Create ring
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(minx, maxy)
        ring.AddPoint(minx, miny)
        ring.AddPoint(maxx, miny)
        ring.AddPoint(maxx, maxy)
        ring.AddPoint(minx, maxy)

        # Create polygon
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        index_record.SetGeometry(poly)

        layer.CreateFeature(index_record)

        index_record.Destroy()

        del raster

    source.Destroy()


def destroy_dummy_index(filename):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(filename):
        driver.DeleteDataSource(filename)


class TestGeoFeatureStorage(unittest.TestCase):
    def setUp(self):
        self.mock = moto.mock_s3()
        self.mock.start()

        s3 = boto3.resource('s3')
        s3.Bucket(TEST_BUCKET_NAME).create()

        # create raster feature
        self.test_key = 'raster/fujisan_10m.tif'

        s3.Object(TEST_BUCKET_NAME, self.test_key).upload_file(
            os.path.join(DATA_DIRECTORY, self.test_key))

        raster_features = [
            (self.test_key, os.path.join(DATA_DIRECTORY, self.test_key))]

        # create index
        self.tempdir = tempfile.mkdtemp()
        create_dummy_index(self.tempdir, raster_features)

        for _, _, filenames in os.walk(self.tempdir):
            for filename in filenames:
                s3.Object(TEST_BUCKET_NAME, filename).upload_file(
                    os.path.join(self.tempdir, filename))

    def tearDown(self):
        destroy_dummy_index(self.tempdir)
        self.mock.stop()

    def test_basic(self):
        storage = S3RasterFeatureStorage(bucket=TEST_BUCKET_NAME)

        test_key = self.test_key
        self.assertTrue(storage.has(test_key))
        self.assertIsInstance(storage.get(test_key), gdal.Dataset)

        storage.delete(test_key)
        self.assertIsNone(storage.get(test_key))
        self.assertFalse(storage.has(test_key))

        storage.close()

    def test_query(self):
        storage = S3RasterFeatureStorage(bucket=TEST_BUCKET_NAME)

        test_envelope = (138.6958690, 35.3309600, 138.7655640, 35.3989940)
        for raster_key in storage.query(test_envelope, crs='EPSG:4326'):
            raster = storage.get(raster_key)

            self.assertEqual(self.test_key, raster_key)
            self.assertIsInstance(raster, gdal.Dataset)
