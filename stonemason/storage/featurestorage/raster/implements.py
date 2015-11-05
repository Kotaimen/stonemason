# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/4/15'

import logging
import numpy as np

from osgeo import gdal, osr, gdalconst

from stonemason.pyramid.geo import Envelope
from stonemason.storage.backends.s3 import S3Storage
from stonemason.storage.backends.disk import DiskStorage

from ..concept import FeatureStorageImpl

from .mapper import SimpleFeatureKeyMode
from .serializer import RasterFeatureSerializer
from .indexer import ShpSpatialIndex


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

    def make_envelope(self, size):
        minx, maxy = self.origin
        resx, resy = self.resolution
        sizex, sizey = size

        maxx = minx + resx * sizex
        miny = maxy - resy * sizey

        return minx, miny, maxx, maxy

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


class RasterDataDomain(object):
    """Base Raster Data Domain

    Data traits of raster data source. Difference raster data have different
    data type. For example, elevation data  may have a data type of Float32
    while image data may have it of Byte.

    Available raster data type:

        ============    =============================
        ``byte``        :data:`gdalconst.GDT_Byte`
        ``uint16``      :data:`gdalconst.GDT_UInt16`
        ``int16``       :data:`gdalconst.GDT_Int16`
        ``uint32``      :data:`gdalconst.GDT_UInt32`
        ``int32``       :data:`gdalconst.GDT_Int32`
        ``float32``     :data:`gdalconst.GDT_Float32`
        ``float64``     :data:`gdalconst.GDT_Float64`
        ``cint16``      :data:`gdalconst.GDT_CInt16`
        ``cint32``      :data:`gdalconst.GDT_CInt32`
        ``cfloat32``    :data:`gdalconst.GDT_CFloat32`
        ``cfloat64``    :data:`gdalconst.GDT_CFloat64`
        ============    =============================

    """

    #: Number of data bands. Default value is ``1``.
    DIMENSION = 1

    #: Value for invalid data in the raster data source. Default value is ``-1``.
    NODATAVALUE = -9999

    #: Data type of pixel value. Default value is ``int32``.
    DATA_TYPE = 'int32'


class RGBDataDomain(RasterDataDomain):
    """RGB Data Domain

    Attributes of a data source with Red, Green, and Blue bands.
    """

    #: Number of data bands.
    DIMENSION = 3

    #: Value for invalid data in the raster data source.
    NODATAVALUE = 0

    #: Data type of pixel value.
    DATA_TYPE = 'byte'


class ElevationDataDomain(RasterDataDomain):
    """Elevation Data Domain

    Attributes of a data source with elevation data.
    """

    #: Number of data bands.
    DIMENSION = 1

    #: Value for invalid data in the raster data source.
    NODATAVALUE = np.finfo(np.float32).min.item()

    #: Data type of pixel value.
    DATA_TYPE = 'float32'


class RasterStorageImpl(FeatureStorageImpl):
    def __init__(self, key_mode, serializer, storage, indexer, domain):
        FeatureStorageImpl.__init__(self, key_mode, serializer, storage)
        self._indexer = indexer
        self._domain = domain

    def intersection(self, envelope, crs='EPSG:4326', size=(256, 256)):
        """Get raster data of the specific area.

        :param crs: coordinate reference system of the return data.
        :type crs: str

        :param envelope: data bounding box represented by a tuple of four
            coordinates ``(left, bottom, right, top)``.
        :type envelope: tuple

        :param size: pixel size of output envelope represented by a tuple
            of width and height. For example, ``(width, height)``

        :return: a array of raster data with a shape like:

            .. math::

                (domain.DIMENSION \\times height \\times width)

        :rtype: numpy.array

        """
        domain = self._domain

        # create target raster dataset
        driver = gdal.GetDriverByName('MEM')

        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(crs)
        target_projection = target_crs.ExportToWkt()

        target_transform = GeoTransform.from_envelope(envelope, size)
        target_width, target_height = size
        target_band_num = domain.DIMENSION

        data_type = gdal.GetDataTypeByName(domain.DATA_TYPE)
        if data_type == gdalconst.GDT_Unknown:
            raise RuntimeError('Unknown data type %s' % domain.DATA_TYPE)

        target = driver.Create(
            '', target_width, target_height, target_band_num, data_type)

        try:
            # initialize
            assert isinstance(target, gdal.Dataset)
            target.SetGeoTransform(target_transform.make_tuple())
            target.SetProjection(target_projection)
            for band_no in range(1, target_band_num + 1):
                band = target.GetRasterBand(band_no)
                assert isinstance(band, gdal.Band)
                band.SetNoDataValue(domain.NODATAVALUE)
                band.Fill(domain.NODATAVALUE)

            # set query bounding geometry
            ctl_envelope = Envelope(*target_transform.make_envelope(size))
            ctl_envelope_geom = ctl_envelope.to_geometry(srs=target_crs)
            if not target_crs.IsSame(self._indexer.crs):
                ctl_envelope_geom.TransformTo(self._indexer.crs)
            ctl_envelope = Envelope.from_ogr(ctl_envelope_geom.GetEnvelope())
            ctl_transform = GeoTransform.from_envelope(ctl_envelope, size)

            # retrieve source data
            for raster_key in self._indexer.intersection(envelope, crs):
                logging.debug('Reading: %s' % raster_key)

                source = self.get(raster_key)
                if source is None:
                    raise KeyError(raster_key)

                try:
                    source_projection = source.GetProjection()
                    source_transform = GeoTransform.from_tuple(
                        source.GetGeoTransform())

                    # find resample method.
                    resample_method = self._find_resample_method(
                        source_transform.resolution,
                        ctl_transform.resolution)

                    ret = gdal.ReprojectImage(source,
                                              target,
                                              source_projection,
                                              target_projection,
                                              resample_method,
                                              1024)
                    if ret != 0:
                        logging.debug('Warp Error: %s' % raster_key)

                finally:
                    # close source data
                    source = None

            result = []
            for band_no in range(1, target.RasterCount + 1):
                band = target.GetRasterBand(band_no)
                # TODO: consider removing this
                # try:
                #     gdal.FillNodata(band, None, 100, 0)
                # except RuntimeError:
                #     # gdal raises exception if failed to remove temporary files,
                #     # however FillNodata still works if we just ignore it.
                #     pass
                result.append(band.ReadAsArray())

            return np.array(result)

        finally:
            # close target data
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


class ElevationDiskStorage(RasterStorageImpl):
    def __init__(self, root='', index='index.shp'):
        storage = DiskStorage()

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index)

        domain = ElevationDataDomain()

        RasterStorageImpl.__init__(self,
                                   key_mode=key_mode,
                                   serializer=serializer,
                                   storage=storage,
                                   indexer=indexer,
                                   domain=domain)


class RGBDiskStorage(RasterStorageImpl):
    def __init__(self, root='', index='index.shp'):
        storage = DiskStorage()

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index)

        domain = RGBDataDomain()

        RasterStorageImpl.__init__(self,
                                   key_mode=key_mode,
                                   serializer=serializer,
                                   storage=storage,
                                   indexer=indexer,
                                   domain=domain)


class ElevationS3Storage(RasterStorageImpl):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False, index='index.shp'):
        storage = S3Storage(access_key=access_key, secret_key=secret_key,
                            bucket=bucket, policy=policy,
                            reduced_redundancy=reduced_redundancy)

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index)

        domain = ElevationDataDomain()

        RasterStorageImpl.__init__(self,
                                   key_mode=key_mode,
                                   serializer=serializer,
                                   storage=storage,
                                   indexer=indexer,
                                   domain=domain)


class RGBS3Storage(RasterStorageImpl):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False, index='index.shp'):
        storage = S3Storage(access_key=access_key, secret_key=secret_key,
                            bucket=bucket, policy=policy,
                            reduced_redundancy=reduced_redundancy)

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index)

        domain = RGBDataDomain()

        RasterStorageImpl.__init__(self,
                                   key_mode=key_mode,
                                   serializer=serializer,
                                   storage=storage,
                                   indexer=indexer,
                                   domain=domain)


def create_raster_storage(prototype, **kwargs):
    if prototype == 'elevation.disk':
        return ElevationDiskStorage(**kwargs)
    elif prototype == 'elevation.s3':
        return ElevationS3Storage(**kwargs)
    elif prototype == 'rgb.disk':
        return RGBDiskStorage(**kwargs)
    elif prototype == 'rgb.s3':
        return RGBS3Storage(**kwargs)
    else:
        raise ValueError('Unknown prototype: %s' % prototype)
