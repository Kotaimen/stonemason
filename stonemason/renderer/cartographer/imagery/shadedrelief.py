# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/15'

import os
import math
import inspect
import tempfile

import numpy as np
import skimage
import skimage.exposure

from PIL import Image, ImageFilter
from scipy import ndimage
from osgeo import ogr, gdal, osr, gdalconst

from ...layerexpr import ImageryLayer
from ...feature import ImageFeature
from ...context import RenderContext

GDAL_VERSION_NUM = int(gdal.VersionInfo('VERSION_NUM'))
if GDAL_VERSION_NUM < 1100000:
    raise ImportError('ERROR: Require GDAL 1.10.0 or above')

gdal.UseExceptions()
ogr.UseExceptions()

gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

MAX_SCALE = 255

VRT_SIMPLE_SOURCE_TEMPLATE = """
<SimpleSource>
    <SourceFilename relativeToVRT="1">%(filename)s</SourceFilename>
    <SourceBand>%(band)d</SourceBand>
</SimpleSource>
"""


class RasterDataSource(object):
    NODATA_VALUE = np.finfo(np.float32).min.item()

    def __init__(self, index):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        self._basedir = os.path.dirname(index)
        self._index_shp = driver.Open(index, gdalconst.GA_ReadOnly)
        if self._index_shp is None:
            raise RuntimeError('Index not found: %s' % index)

        self._index = self._index_shp.GetLayer(0)
        if self._index is None:
            raise RuntimeError('Index layer not found!')

    def query(self, proj, envelope, size, bands=[1]):
        if len(bands) == 0:
            return []

        if isinstance(bands, int):
            bands = [bands]

        left, bottom, right, top = envelope

        envelope_wkt = "POLYGON ((" \
                       "%(lt)f %(bm)f," \
                       "%(lt)f %(tp)f," \
                       "%(rt)f %(tp)f," \
                       "%(rt)f %(bm)f," \
                       "%(lt)f %(bm)f" \
                       "))" % dict(lt=left, bm=bottom, rt=right, tp=top)

        filter_geom = ogr.CreateGeometryFromWkt(envelope_wkt)
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(proj)

        # transform filter envelope crs to index crs
        index_crs = self._index.GetSpatialRef()
        if not target_crs.IsSame(index_crs):
            transform = osr.CoordinateTransformation(target_crs, index_crs)
            filter_geom.Transform(transform)

        filter_envelope = filter_geom.GetEnvelope()
        filter_res = (filter_envelope[1] - filter_envelope[0]) / size[0]

        try:

            # create memory data source
            target_width, target_height = size
            target_res_x = (right - left) / target_width
            target_res_y = (top - bottom) / target_height
            target_geotransform = \
                left, target_res_x, 0.0, top, 0.0, -target_res_y
            target_projection = target_crs.ExportToWkt()

            driver = gdal.GetDriverByName('MEM')
            target = driver.Create('',
                                   target_width, target_height, len(bands),
                                   gdal.GDT_Float32)
            target.SetGeoTransform(target_geotransform)
            target.SetProjection(target_projection)

            for band_no in range(1, target.RasterCount + 1):
                target_band = target.GetRasterBand(band_no)  # start from 1
                target_band.SetNoDataValue(self.NODATA_VALUE)
                target_band.Fill(self.NODATA_VALUE)

            # find data source intersection with target envelope
            self._index.SetSpatialFilter(filter_geom)

            for n, feature in enumerate(self._index):

                location = os.path.join(
                    self._basedir, feature.GetField('location'))
                # print n, location
                try:
                    source = gdal.OpenShared(location, gdalconst.GA_ReadOnly)
                    source_projection = source.GetProjection()
                    source_geotransform = source.GetGeoTransform()

                    # create vrt for target band
                    width, height = source.RasterXSize, source.RasterYSize
                    vrt_driver = gdal.GetDriverByName('VRT')
                    vrt_source = vrt_driver.Create(
                        '', width, height, len(bands), gdalconst.GDT_Float32)
                    vrt_source.SetGeoTransform(source_geotransform)
                    vrt_source.SetProjection(proj)

                    for n, band_no in enumerate(bands, start=1):
                        # add source band to vrt band
                        vrt_band = vrt_source.GetRasterBand(n)
                        nodata = source.GetRasterBand(band_no).GetNoDataValue()
                        if nodata is not None:
                            vrt_band.SetNoDataValue(float(nodata))

                        simple_source = VRT_SIMPLE_SOURCE_TEMPLATE % dict(
                            filename=location,
                            band=band_no,
                            src_width=width,
                            src_height=height,
                            dst_width=width,
                            dst_height=height,
                        )
                        metadata = vrt_band.GetMetadata()
                        metadata['source_%d' % n] = simple_source
                        vrt_band.SetMetadata(metadata, 'vrt_sources')

                    # find resample methods.
                    src_res_x = source_geotransform[1]
                    if src_res_x > filter_res:
                        # scale down
                        resample = gdalconst.GRA_CubicSpline
                    else:
                        # scale up
                        resample = gdalconst.GRA_Bilinear

                    ret = gdal.ReprojectImage(vrt_source,
                                              target,
                                              source_projection,
                                              target_projection,
                                              resample,
                                              1024)
                finally:
                    vrt_source = None
                    source = None

            array_list = []
            for band_no in range(1, target.RasterCount + 1):
                target_band = target.GetRasterBand(band_no)
                try:
                    gdal.FillNodata(target_band, None, 100, 0)
                except RuntimeError:
                    # gdal raises exception for missing temporary files to remove,
                    # however FillNodata still works.
                    pass

                array = target_band.ReadAsArray()
                array_list.append(array)

            return array_list

        finally:
            target = None

    def close(self):
        self._index_shp = None

    def __enter__(self):
        yield self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def aspect_and_slope(elevation, resx, resy, zfactor, scale):
    """ create aspect and slope from raster """
    kernel = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
    dx = ndimage.convolve(elevation, kernel / (8. * resx), mode='nearest')

    kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    dy = ndimage.convolve(elevation, kernel / (8. * resy), mode='nearest')

    slope = np.arctan(float(zfactor) / float(scale) * np.hypot(dx, dy))
    aspect = math.pi / 2. - np.arctan2(dy, -dx)

    return aspect, slope


def hillshade(aspect, slope, azimuth, altitude):
    """ create hillshade from aspect and slope """
    zenith = math.radians(90. - float(altitude) % 360.)
    azimuth = math.radians(float(azimuth))

    shade = 1. * ((math.cos(zenith) * np.cos(slope)) +
                  (math.sin(zenith) * np.sin(slope) * np.cos(azimuth - aspect)))

    shade[shade < 0] = 0.
    return shade


class ShadedRelief(ImageryLayer):
    PROTOTYPE = 'shadedrelief'

    def __init__(self, name, index,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=45,
                 buffer=16,
                 sigmoid_cutoff=0.8,
                 sigmoid_gain=2,
                 sigmoid_base=0.05,
                 sharpen_radius=1,
                 sharpen_percent=100,
                 sharpen_threshold=3
                 ):
        ImageryLayer.__init__(self, name)
        self._source_index = index
        self._zfactor = zfactor
        self._scale = scale
        self._azimuth = azimuth
        self._altitude = altitude
        self._buffer = buffer

        self._sigmoid_cutoff = sigmoid_cutoff
        self._sigmoid_gain = sigmoid_gain
        self._sigmoid_base = sigmoid_base

        self._sharpen_radius = sharpen_radius
        self._sharpen_percent = sharpen_percent
        self._sharpen_threshold = sharpen_threshold

    def array2pil(self, array, width, height):
        #        array = (MAX_SCALE * detail).astype(np.ubyte)

        # cropping to requested map size
        array = array[
                self._buffer:width + self._buffer,
                self._buffer:height + self._buffer
                ]

        image = skimage.img_as_ubyte(array)

        # convert arrary to pil image
        pil_image = Image.fromarray(image, mode='L')

        return pil_image

    def render(self, context):
        assert isinstance(context, RenderContext)

        left, bottom, right, top = context.map_bbox
        width, height = context.map_size

        # calculate map resolution
        res_x = (right - left) / width
        res_y = (top - bottom) / height

        # calculate buffered envelope size
        buffer_x = res_x * self._buffer
        buffer_y = res_y * self._buffer

        # calculate buffered map envelope
        envelope = (left - buffer_x,
                    bottom - buffer_y,
                    right + buffer_x,
                    top + buffer_y)
        # calculate buffered map size
        envelope_size = width + 2 * self._buffer, height + 2 * self._buffer

        # query elevation data in target envelope
        source_index = self._source_index
        if inspect.isfunction(self._source_index):
            source_index = self._source_index(res_x, res_y)

        source = RasterDataSource(source_index)
        elevation = source.query(
            context.map_proj, envelope, envelope_size, bands=[1])[0]

        # calculate hill shading
        zfactor = self._zfactor
        if inspect.isfunction(zfactor):
            zfactor = zfactor(res_x, res_y)

        aspect, slope = aspect_and_slope(elevation,
                                         res_x, res_y, zfactor, self._scale)

        detail = hillshade(aspect, slope, self._azimuth, self._altitude)

        specular = hillshade(aspect, slope, 300 - self._azimuth, self._altitude)

        # exposure
        detail = skimage.exposure.adjust_sigmoid(detail,
                                                 cutoff=self._sigmoid_cutoff,
                                                 gain=self._sigmoid_gain)

        specular = skimage.exposure.adjust_sigmoid(specular,
                                                   cutoff=self._sigmoid_cutoff,
                                                   gain=self._sigmoid_gain / 2.)

        detail_image = self.array2pil(detail, width, height)
        specular_image = self.array2pil(specular, width, height)

        mask = elevation / 1600.
        mask[mask > 1] = 1
        mask[mask < 0] = 0

        mask_image = self.array2pil(mask, width, height)

        relief_image = Image.composite(detail_image, specular_image, mask_image)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=relief_image)

        return feature


class ColoredRelief(ImageryLayer):
    PROTOTYPE = 'coloredrelief'

    def __init__(self, name, index, color_bands=None, alpha_band=None,
                 buffer=0):
        ImageryLayer.__init__(self, name)

        if color_bands is None:
            color_bands = [1, 2, 3]

        if len(color_bands) != 3:
            raise RuntimeError('Insufficient color bands number!')

        self._source = RasterDataSource(index)
        self._color_bands = color_bands
        self._alpha_band = alpha_band
        self._buffer = buffer

    def render(self, context):
        left, bottom, right, top = context.map_bbox
        width, height = context.map_size

        # calculate map resolution
        res_x = (right - left) / width
        res_y = (top - bottom) / height

        # calculate buffered envelope size
        buffer_x = res_x * self._buffer
        buffer_y = res_y * self._buffer

        # calculate buffered map envelope
        envelope = (left - buffer_x,
                    bottom - buffer_y,
                    right + buffer_x,
                    top + buffer_y)
        # calculate buffered map size
        envelope_size = width + 2 * self._buffer, height + 2 * self._buffer

        # query elevation data in target envelope
        query_bands = self._color_bands
        if self._alpha_band is not None:
            query_bands.append(self._alpha_band)

        bands = self._source.query(
            context.map_proj, envelope, envelope_size, bands=query_bands)

        result = np.dstack(bands).astype(np.ubyte)
        result = result[
                 self._buffer:width + self._buffer,
                 self._buffer:height + self._buffer]

        if len(bands) == 4:
            pil_image = Image.fromarray(result, 'RGBA')
        else:
            pil_image = Image.fromarray(result, 'RGB')
            pil_image = pil_image.convert('RGBA')

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature
