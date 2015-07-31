# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/27/15'

import os
import logging
import tempfile

import numpy as np
from osgeo import ogr, gdal, osr, gdalconst

from stonemason.pyramid.geo import Envelope

ogr.UseExceptions()
osr.UseExceptions()
gdal.UseExceptions()

GDAL_VERSION_NUM = int(gdal.VersionInfo('VERSION_NUM'))
if GDAL_VERSION_NUM < 1100000:
    raise ImportError('ERROR: Require GDAL 1.10.0 or above')

gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())


class GeoTransform(object):
    def __init__(self, origin, resolution, skew=(0, 0)):
        self._origin = origin
        self._resolution = resolution
        self._skew = skew

    @property
    def origin(self):
        return self._origin

    @property
    def resolution(self):
        return self._resolution

    @property
    def skew(self):
        return self._skew

    def make_tuple(self):
        transform = self._origin[0], self._resolution[0], self._skew[0], \
                    self._origin[1], self._skew[1], -self._resolution[1]
        return transform

    @staticmethod
    def from_tuple(transform):
        origin = transform[0], transform[3]
        resolution = transform[1], -transform[5]
        skew = transform[2], transform[4]

        return GeoTransform(origin, resolution, skew)

    @staticmethod
    def from_envelope(envelope, size):
        left, bottom, right, top = envelope
        width, height = size

        res_x = (right - left) / width
        res_y = (top - bottom) / height
        resolution = res_x, res_y

        origin = left, top

        return GeoTransform(origin, resolution)


class DataDomain(object):
    DIMENSION = 1
    NODATAVALUE = -1
    DATA_TYPE = gdalconst.GDT_Int32


class GreyScaleDomain(DataDomain):
    DIMENSION = 1
    NODATAVALUE = -1
    DATA_TYPE = gdalconst.GDT_Byte


class RGBDomain(DataDomain):
    DIMENSION = 3
    NODATAVALUE = -1
    DATA_TYPE = gdalconst.GDT_Byte


class ElevationDomain(GreyScaleDomain):
    DIMENSION = 1
    NODATAVALUE = np.finfo(np.float32).min.item()
    DATA_TYPE = gdalconst.GDT_Float32


class RasterDataSource(object):
    def __init__(self, index, domain=None):

        driver = ogr.GetDriverByName("ESRI Shapefile")
        self._basedir = os.path.dirname(index)
        self._metadata = driver.Open(index, gdalconst.GA_ReadOnly)
        if self._metadata is None:
            raise RuntimeError('Index file not found: %s' % index)

        self._index = self._metadata.GetLayer(0)
        if self._index is None:
            raise RuntimeError('Index layer not found!')

        if domain is None:
            domain = DataDomain()
        self._domain = domain

    def query(self, crs, envelope, size):
        # calculate result information
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(crs)
        target_projection = target_crs.ExportToWkt()

        target_transform = GeoTransform.from_envelope(envelope, size)
        target_width, target_height = size
        target_band_num = self._domain.DIMENSION

        try:
            # create target raster dataset
            driver = gdal.GetDriverByName('MEM')
            target = driver.Create(
                '', target_width, target_height, target_band_num,
                self._domain.DATA_TYPE)
            assert isinstance(target, gdal.Dataset)
            target.SetGeoTransform(target_transform.make_tuple())
            target.SetProjection(target_projection)
            for band_no in range(1, target_band_num + 1):
                band = target.GetRasterBand(band_no)
                assert isinstance(band, gdal.Band)
                band.SetNoDataValue(self._domain.NODATAVALUE)
                band.Fill(self._domain.NODATAVALUE)

            # set query bounding geometry
            query_geom = Envelope(*envelope).to_geometry(srs=target_crs)
            query_crs = self._index.GetSpatialRef()
            if not target_crs.IsSame(query_crs):
                query_geom.TransformTo(query_crs)
            query_envelope = Envelope.from_ogr(query_geom.GetEnvelope())
            query_transform = GeoTransform.from_envelope(query_envelope, size)

            self._index.SetSpatialFilter(query_geom)

            # retrieve source data and fill target area
            for n, record in enumerate(self._index):
                location = os.path.join(
                    self._basedir, record.GetField('location'))
                logging.debug('Reading:[%d]%s' % (n, location))
                try:
                    source = gdal.OpenShared(location, gdalconst.GA_ReadOnly)
                    source_projection = source.GetProjection()
                    source_transform = GeoTransform.from_tuple(
                        source.GetGeoTransform())

                    # find resample method.
                    resample_method = self._find_resample_method(
                        source_transform.resolution,
                        query_transform.resolution,
                    )

                    ret = gdal.ReprojectImage(source,
                                              target,
                                              source_projection,
                                              target_projection,
                                              resample_method,
                                              1024)
                    if ret != 0:
                        logging.debug('Warp Error:[%d]%s' % (n, location))

                finally:
                    source = None

            result = []
            for band_no in range(1, target.RasterCount + 1):
                band = target.GetRasterBand(band_no)
                try:
                    gdal.FillNodata(band, None, 100, 0)
                except RuntimeError:
                    # gdal raises exception if failed to remove temporary files,
                    # however FillNodata still works if we just ignore it.
                    pass
                result.append(band.ReadAsArray())

            return np.array(result)

        finally:
            target = None

    def _find_resample_method(self, resolution_a, resolution_b):
        # find resample method.
        if resolution_a[0] > resolution_b[0]:
            # scale down
            resample_method = gdalconst.GRA_CubicSpline
        else:
            # scale up
            resample_method = gdalconst.GRA_Bilinear
        return resample_method

    def close(self):
        self._index = None
        self._metadata = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ElevationDataSource(RasterDataSource):
    def __init__(self, index):
        domain = ElevationDomain()
        RasterDataSource.__init__(self, index, domain=domain)


class RGBImageDataSource(RasterDataSource):
    def __init__(self, index):
        domain = RGBDomain()
        RasterDataSource.__init__(self, index, domain=domain)
