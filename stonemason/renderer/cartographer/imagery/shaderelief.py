# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/15'

import os
import math
import numpy as np
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

MAX_SCALE = 255


class RasterDataSource(object):
    NODATA_VALUE = np.finfo(np.float32).min.item()

    def __init__(self, index):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        self._basedir = os.path.dirname(index)
        self._index_shp = driver.Open(index, gdalconst.GA_ReadOnly)
        self._index = self._index_shp.GetLayerByName('index')

    def query(self, proj, envelope, size):
        left, bottom, right, top = envelope

        envelope_wkt = "POLYGON ((" \
                       "%(lt)f %(bm)f," \
                       "%(lt)f %(tp)f," \
                       "%(rt)f %(tp)f," \
                       "%(rt)f %(bm)f," \
                       "%(lt)f %(bm)f" \
                       "))" % dict(lt=left, bm=bottom, rt=right, tp=top)

        filter_envelope = ogr.CreateGeometryFromWkt(envelope_wkt)
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(proj)

        index_crs = self._index.GetSpatialRef()
        if not target_crs.IsSame(index_crs):
            transform = osr.CoordinateTransformation(target_crs, index_crs)
            filter_envelope.Transform(transform)

        target_width, target_height = size
        target_res_x = (right - left) / target_width
        target_res_y = (top - bottom) / target_height
        target_geotransform = left, target_res_x, 0.0, top, 0.0, -target_res_y
        target_projection = target_crs.ExportToWkt()

        driver = gdal.GetDriverByName('MEM')
        target = driver.Create('',
                               target_width, target_height, 1,
                               gdal.GDT_Float32)
        target.SetGeoTransform(target_geotransform)
        target.SetProjection(target_projection)

        target_band = target.GetRasterBand(1)
        target_band.SetNoDataValue(self.NODATA_VALUE)
        target_band.SetColorInterpretation(gdalconst.GCI_Undefined)
        target_band.Fill(self.NODATA_VALUE)

        self._index.SetSpatialFilter(filter_envelope)

        for n, feature in enumerate(self._index):
            # iterate raster data files covering the target area

            location = os.path.join(self._basedir, feature.GetField('location'))
            print n, location

            source = gdal.OpenShared(location, gdalconst.GA_ReadOnly)
            source_projection = source.GetProjection()

            resample = gdalconst.GRA_Bilinear

            ret = gdal.ReprojectImage(source,
                                      target,
                                      source_projection,
                                      target_projection,
                                      resample,
                                      1024)

            source = None

        gdal.FillNodata(
            target_band,  # targetBand
            None,  # maskBand
            100,  # maxSearchDist
            0)  # smoothingIterations

        array = target.ReadAsArray()

        target = None

        return array

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


class ShadeRelief(ImageryLayer):
    PROTOTYPE = 'shaderelief'

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
        self._source = RasterDataSource(index)
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
        elevation = self._source.query(
            context.map_proj, envelope, envelope_size)

        # calculate hill shading
        zfactor = self._zfactor
        aspect, slope = aspect_and_slope(
            elevation, res_x, res_y, zfactor, self._scale)
        detail = hillshade(aspect, slope, self._azimuth, self._altitude)

        # exposure
        detail = skimage.exposure.adjust_sigmoid(detail,
                                                 cutoff=self._sigmoid_cutoff,
                                                 gain=self._sigmoid_gain,
                                                 inv=False) + self._sigmoid_base


        # tone mapping
        array = (MAX_SCALE * detail).astype(np.ubyte)

        # cropping to requested map size
        array = array[
                self._buffer:width + self._buffer,
                self._buffer:height + self._buffer
                ]

        # convert arrary to pil image
        pil_image = Image.fromarray(array, mode='L')
        pil_image = pil_image.convert('RGBA')

        pil_image = pil_image.filter(
            ImageFilter.UnsharpMask(
                radius=self._sharpen_radius,
                percent=self._sharpen_percent,
                threshold=self._sharpen_threshold
            ))

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature
