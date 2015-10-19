# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.datasource.raster
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of raster data sources.
"""
__author__ = 'ray'
__date__ = '7/27/15'

import re
import os
import logging
import tempfile

import boto3
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
    NODATAVALUE = -1

    #: Data type of pixel value. Default value is ``int32``.
    DATA_TYPE = 'int32'


class RasterDataSource(object):
    """Base class of Raster Data Source

    `RasterDataSource` is a data store that provides raster data in the request
    envelope. It manages a set of raster files on the disk through a index
    shapefile. Raster files are indexed on their bounding boxes in this file.

    Data domain is used to provide information about specific properties about
    raster data.

    A user could query data by providing coordinate reference system, envelope
    and pixel size.

    :param index: location of index shapefile.
    :type index: str

    :param domain: data domain
    :type domain: :class:`~stonemason.renderer.datasource.DataDomain`

    """

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

    @property
    def domain(self):
        """Get data domain of the raster data source.

        :return: return data domain of the raster data source.
        :rtype: :class:`~stonemason.renderer.datasource.DataDomain`
        """
        return self._domain

    def query(self, crs, envelope, size):
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

        # calculate result information
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(crs)
        target_projection = target_crs.ExportToWkt()

        target_transform = GeoTransform.from_envelope(envelope, size)
        target_width, target_height = size
        target_band_num = domain.DIMENSION


        # create target raster dataset
        driver = gdal.GetDriverByName('MEM')

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
            query_geom = Envelope(*envelope).to_geometry(srs=target_crs)
            query_crs = self._index.GetSpatialRef()
            if not target_crs.IsSame(query_crs):
                query_geom.TransformTo(query_crs)
            query_envelope = Envelope.from_ogr(query_geom.GetEnvelope())
            query_transform = GeoTransform.from_envelope(query_envelope, size)

            self._index.SetSpatialFilter(query_geom)

            # retrieve source data
            for n, record in enumerate(self._index):
                location = os.path.join(
                    self._basedir, record.GetField('location'))
                logging.debug('Reading:[%d]%s' % (n, location))

                source = gdal.OpenShared(location, gdalconst.GA_ReadOnly)
                try:
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

    def close(self):
        """Close the data source"""
        self._index = None
        self._metadata = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class S3RasterDataSource(object):
    def __init__(self, bucket_name, index_path, domain=None):

        self._s3 = boto3.resource('s3')

        self._bucket = self._s3.Bucket(bucket_name)
        self._bucket.load()  # test bucket existence

        # download index file
        self._index_path = index_path
        index_name = os.path.splitext(index_path)[0]
        self._tmp_index_name = tempfile.mktemp()
        for ext in ['.shp', '.dbf', '.prj', '.shx']:
            index_obj = self._s3.Object(self._bucket.name, index_name + ext)
            index_obj.download_file(self._tmp_index_name + ext)

        driver = ogr.GetDriverByName("ESRI Shapefile")

        self._metadata = driver.Open(self._tmp_index_name + '.shp', gdalconst.GA_ReadOnly)
        if self._metadata is None:
            raise RuntimeError('Index file not found: %s' % self._tmp_index_name)

        self._index = self._metadata.GetLayer(0)
        if self._index is None:
            raise RuntimeError('Index layer not found!')

        if domain is None:
            domain = DataDomain()
        self._domain = domain

    @property
    def domain(self):
        """Get data domain of the raster data source.

        :return: return data domain of the raster data source.
        :rtype: :class:`~stonemason.renderer.datasource.DataDomain`
        """
        return self._domain

    def query(self, crs, envelope, size):
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

        # calculate result information
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(crs)
        target_projection = target_crs.ExportToWkt()

        target_transform = GeoTransform.from_envelope(envelope, size)
        target_width, target_height = size
        target_band_num = domain.DIMENSION


        # create target raster dataset
        driver = gdal.GetDriverByName('MEM')

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
            query_geom = Envelope(*envelope).to_geometry(srs=target_crs)
            query_crs = self._index.GetSpatialRef()
            if not target_crs.IsSame(query_crs):
                query_geom.TransformTo(query_crs)
            query_envelope = Envelope.from_ogr(query_geom.GetEnvelope())
            query_transform = GeoTransform.from_envelope(query_envelope, size)

            self._index.SetSpatialFilter(query_geom)

            # retrieve source data
            for n, record in enumerate(self._index):
                location = record.GetField('location')
                logging.debug('Reading:[%d]%s' % (n, location))

                location = os.path.normpath(os.path.join(os.path.dirname(self._index_path), location))

                source_object = self._s3.Object(self._bucket.name, location)

                source_filename = tempfile.mktemp()
                source_object.download_file(source_filename)

                source = gdal.OpenShared(source_filename, gdalconst.GA_ReadOnly)
                try:
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
                    # close source data
                    source = None
                    if os.path.exists(source_filename):
                        os.remove(source_filename)

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

    def close(self):
        """Close the data source"""
        self._index = None
        self._metadata = None

        for ext in ['.shp', '.dbf', '.prj', '.shx']:
            temp_index_obj = self._tmp_index_name + ext
            os.remove(temp_index_obj)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class RGBDomain(DataDomain):
    """RGB Data Domain

    Attributes of a data source with Red, Green, and Blue bands.
    """

    #: Number of data bands.
    DIMENSION = 3

    #: Value for invalid data in the raster data source.
    NODATAVALUE = -1

    #: Data type of pixel value.
    DATA_TYPE = 'byte'


class ElevationDomain(DataDomain):
    """Elevation Data Domain

    Attributes of a data source with elevation data.
    """

    #: Number of data bands.
    DIMENSION = 1

    #: Value for invalid data in the raster data source.
    NODATAVALUE = np.finfo(np.float32).min.item()

    #: Data type of pixel value.
    DATA_TYPE = 'float32'


def ElevationData(index):
    """Elevation Data Source

    A set of elevation raster data. Subclass of
    :class:`~stonemason.renderer.datasource.RasterDataSource` with
    :class:`~stonemason.renderer.datasource.ElevationDomain`.
    """

    domain = ElevationDomain()
    m = re.match('s3://(?P<bucket>.*?)/(?P<index>.*)', index)
    if m:
        bucket_name = m.group('bucket')
        index_key = m.group('index')
        return S3RasterDataSource(bucket_name, index_key, domain=domain)
    else:
        return RasterDataSource(index, domain=domain)


def RGBImageData(index):
    """RGB Image Data Source

    A set of raster data with red, green and blue bands. Subclass of
    :class:`~stonemason.renderer.datasource.RasterDataSource` with
    :class:`~stonemason.renderer.datasource.RGBDomain`.
    """

    domain = RGBDomain()
    m = re.match('s3://(?P<bucket>.*?)/(?P<index>.*)', index)
    if m:
        bucket_name = m.group('bucket')
        index_key = m.group('index')
        return S3RasterDataSource(bucket_name, index_key, domain=domain)
    else:
        return RasterDataSource(index, domain=domain)
