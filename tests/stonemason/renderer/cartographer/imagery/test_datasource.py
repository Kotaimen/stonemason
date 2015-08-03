# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/29/15'

import os
import unittest

import numpy as np
from osgeo import ogr, gdal, osr, gdalconst

from stonemason.pyramid.geo.tms import Envelope
from stonemason.renderer.cartographer.imagery.datasource import \
    ElevationDomain, ElevationDataSource, GeoTransform

from tests import DATA_DIRECTORY


def save_raster(name, crs, envelope, size, array, domain):
    width, height = size
    assert array.shape == (height, width)

    projection = osr.SpatialReference()
    projection.SetFromUserInput(crs)

    transform = GeoTransform.from_envelope(envelope, size)

    try:
        driver = gdal.GetDriverByName('GTIFF')
        raster = driver.Create(
            name, width, height, domain.DIMENSION, domain.NODATAVALUE)
        assert isinstance(raster, gdal.Dataset)
        raster.SetGeoTransform(transform.make_tuple())
        raster.SetProjection(projection.ExportToWkt())

        for band_no in range(domain.DIMENSION):
            band = raster.GetRasterBand(band_no + 1)
            assert isinstance(band, gdal.Band)
            band.SetNoDataValue(domain.NODATAVALUE)
            band.WriteArray(array[band_no])

        raster.FlushCache()

    finally:
        raster = None


def save_index(name, location, geometry):
    driver = ogr.GetDriverByName('ESRI Shapefile')

    shp = driver.CreateDataSource(name)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    layer = shp.CreateLayer('index', srs, ogr.wkbPolygon)

    field_location = ogr.FieldDefn("location", ogr.OFTString)
    layer.CreateField(field_location)

    feature = ogr.Feature(layer.GetLayerDefn())
    feature.SetField("location", location)
    feature.SetGeometry(geometry)

    layer.CreateFeature(feature)

    feature.Destroy()

    shp.Destroy()


def mock_dem_5m():
    crs = 'WGS84'
    envelope = (138.695869, 35.330960, 138.765564, 35.398994)
    size = (256, 256)

    domain = ElevationDomain()
    name = os.path.join(DATA_DIRECTORY, 'raster', 'fujisan_5m.tif')
    index_name = os.path.join(DATA_DIRECTORY, 'raster', 'index_5m.shp')

    with ElevationDataSource(
            '/Volumes/data/geodata/geodata/Stage/jpn-5m/index.shp') as source:
        elev_5m = source.query(crs, envelope, size)
        save_raster(name, crs, envelope, size, elev_5m, domain)

    save_index(index_name, name, Envelope(*envelope).to_geometry())


def mock_dem_10m():
    crs = 'WGS84'
    envelope = (138.695869, 35.330960, 138.765564, 35.398994)
    size = (256, 256)

    domain = ElevationDomain()
    name = os.path.join(DATA_DIRECTORY, 'raster', 'fujisan_10m.tif')
    index_name = os.path.join(DATA_DIRECTORY, 'raster', 'index_10m.shp')

    with ElevationDataSource(
            '/Volumes/data/geodata/geodata/Stage/JPN10M/index.shp') as source:
        elev_10m = source.query(crs, envelope, size)
        save_raster(name, crs, envelope, size, elev_10m, domain)

    save_index(index_name, name, Envelope(*envelope).to_geometry())


class TestRasterDataSource(unittest.TestCase):
    def setUp(self):
        # mock_dem_5m()
        # mock_dem_10m()
        pass

    def test_query(self):
        crs = 'WGS84'
        envelope = (138.695869, 35.330960, 138.765564, 35.398994)
        size = (256, 256)

        index_name = os.path.join(DATA_DIRECTORY, 'raster', 'index_5m.shp')

        with ElevationDataSource(index_name) as source:
            elev_5m = source.query(crs, envelope, size)[0]

        filename = os.path.join(DATA_DIRECTORY, 'raster', 'fujisan_5m.tif')
        expected = gdal.Open(filename)
        assert isinstance(expected, gdal.Dataset)
        elev_expected = expected.ReadAsArray()

        self.assertTrue(np.all(np.equal(elev_5m, elev_expected)))
