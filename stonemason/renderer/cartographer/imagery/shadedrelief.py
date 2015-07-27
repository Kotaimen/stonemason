# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/15'

import os
import math
import tempfile

from PIL import Image, ImageFilter
from osgeo import ogr, gdal, osr, gdalconst

import numpy as np
from scipy import ndimage

import skimage
import skimage.exposure
import skimage.filters
import skimage.segmentation
import skimage.morphology

from stonemason.renderer.layerexpr import ImageryLayer
from stonemason.renderer.feature import ImageFeature
from stonemason.renderer.context import RenderContext

GDAL_VERSION_NUM = int(gdal.VersionInfo('VERSION_NUM'))
if GDAL_VERSION_NUM < 1100000:
    raise ImportError('ERROR: Require GDAL 1.10.0 or above')

gdal.UseExceptions()
ogr.UseExceptions()

gdal.SetConfigOption('CPL_TMPDIR', tempfile.gettempdir())

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


#
# Helper functions
#

def aspect_and_slope(elevation, resolution, scale, z_factor=1.0):
    """Generate aspect and slope map from given elevation raster.

    :return: Aspect and slope map in a tuple ``(aspect, slope)``.
    :rtype: tuple
    """

    res_x, res_y = resolution
    kernel = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
    dx = ndimage.convolve(elevation, kernel / (8. * res_x), mode='nearest')

    kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    dy = ndimage.convolve(elevation, kernel / (8. * res_y), mode='nearest')

    slope = np.arctan(float(z_factor) / float(scale) * np.hypot(dx, dy))
    aspect = math.pi / 2. - np.arctan2(dy, -dx)

    return aspect, slope


def hill_shading(aspect, slope, azimuth=315, altitude=45):
    """Generate hill shading map from aspect and slope, which are the result of
    :func:`~stonemason.renderer.cartographer.imagery.shadedrelief.aspect_and_slope`.

    :return: Generated shaded relief.
    :rtype: numpy.array
    """
    zenith = math.radians(90. - float(altitude) % 360.)
    azimuth = math.radians(float(azimuth))

    shade = ((math.cos(zenith) * np.cos(slope)) +
             (math.sin(zenith) * np.sin(slope) * np.cos(azimuth - aspect)))

    shade[shade < 0] = 0.
    return shade


def array2pillow(array, width, height, buffer=0):
    """ Convert a numpy array image to PIL image, note only greyscale image is
    supported.

    :param array: Input image.
    :type array: numpy.array

    :param width: Width of the image in pixel.
    :type width: int

    :param height: Height of the image in pixel.
    :param height: int

    :param buffer: Extra buffer size to crop around the given image, default
        is ``0``.
    :type buffer: int

    :return: Converted PIL image.
    :rtype: :class:`PIL.Image.Image`
    """

    # cropping to requested map size
    array = array[buffer:width + buffer, buffer:height + buffer]

    image = skimage.img_as_ubyte(array)

    # convert arrary to pil image
    pil_image = Image.fromarray(image, mode='L')

    return pil_image


def simple_shaded_relief(elevation, resolution, scale=111120,
                         z_factor=1., azimuth=315, altitude=45,
                         cutoff=0.707, gain=4):
    """Render a simple shaded relief.

    :param elevation: Array like digital elevation raster.
    :type elevation: numpy.array

    :param resolution: Resolution of the elevation, in ``(x, y)`` tuple.
    :type resolution: tuple

    :param scale: Ratio of vertical units to horizontal. If the horizontal
        unit of the elevation raster is degrees (e.g: ``WGS84``), set `scale`
        to ``111120`` if the vertical unit is meter, or set to ``370400``
        if vertical unit is feet.
    :type scale: float

    :param z_factor: Vertical exaggeration used to pre-multiply the elevations,
        default value is ``1``, which means no exaggeration.
    :type z_factor: float

    :param azimuth: Azimuth of the light, in degrees.  ``0`` comes from north,
        ``90`` from the east... default value is ``315``.
    :type azimuth: float

    :param altitude: Altitude of the light, in degrees. ``90`` if the light
        comes from top, ``0`` is raking light, default value is ``45``
    :type altitude: float

    :param cutoff: `Cutoff` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``0.707``.
    :type cutoff: float

    :param gain: `Gain` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``5``.
    :type gain: float

    :return: Rendered shaded relief as a image.
    :rtype: numpy.array
    """
    aspect, slope = aspect_and_slope(elevation, resolution, scale=scale,
                                     z_factor=z_factor)
    shading = hill_shading(aspect, slope, azimuth=azimuth, altitude=altitude)

    shading = skimage.exposure.adjust_sigmoid(shading, cutoff=cutoff, gain=gain)

    return shading


def swiss_shaded_relief(elevation, resolution, scale=111120,
                        z_factor=1., azimuth=315, altitude=45,
                        high_relief_cutoff=0.7,
                        high_relief_gain=5,
                        low_relief_cutoff=0.7,
                        low_relief_gain=1,
                        height_mask_range=(0, 3000),
                        height_mask_gamma=0.5
                        ):
    """Render a high quality shaded relief presented by Imhof.

    :param elevation: Array like digital elevation raster.
    :type elevation: numpy.array

    :param resolution: Resolution of the elevation, in ``(x, y)`` tuple.
    :type resolution: tuple

    :param scale: Ratio of vertical units to horizontal. If the horizontal
        unit of the elevation raster is degrees (e.g: ``WGS84``), set `scale`
        to ``111120`` if the vertical unit is meter, or set to ``370400``
        if vertical unit is feet.
    :type scale: float

    :param z_factor: Vertical exaggeration used to pre-multiply the elevations,
        default value is ``1``, which means no exaggeration.
    :type z_factor: float

    :param azimuth: Azimuth of the light, in degrees.  ``0`` comes from north,
        ``90`` from the east... default value is ``315``.
    :type azimuth: float

    :param altitude: Altitude of the light, in degrees. ``90`` if the light
        comes from top, ``0`` is raking light, default value is ``45``
    :type altitude: float

    :param high_relief_cutoff: Sigmoid contrast cutoff of the high elevation
        areas, default value is ``0.7``
    :type high_relief_cutoff: float

    :param high_relief_gain: Sigmoid contrast gain of the high elevation
        areas, default value is ``5``.
    :type high_relief_gain: float

    :param low_relief_cutoff: Sigmoid contrast cutoff of the low elevation
        areas, default value is ``0.7``.
    :type low_relief_cutoff: float

    :param low_relief_gain: Sigmoid contrast gain of the low elevation
        areas, default value is ``1``.
    :type low_relief_gain: float

    :param height_mask_range: A tuple specifies range of height mask in
        meters, default is ``(0, 3000)``.
    :type height_mask_range: tuple

    :param height_mask_gamma: Gamma correction of the height mask,
        default is ``0.5``.
    :type height_mask_gamma: float

    :return: Rendered shaded relief as a image.
    :rtype: numpy.array
    """

    aspect, slope = aspect_and_slope(elevation, resolution, scale=scale,
                                     z_factor=z_factor)

    # use different lighting angle to calculate different exposures
    assert azimuth > 180
    diffuse = hill_shading(aspect, slope, azimuth, 35)
    detail = hill_shading(aspect, slope, azimuth - 180, 50)
    specular = hill_shading(aspect, slope, azimuth, 90)

    # toning by blend different exposures together:
    #    diffuse <-a- detail <-b- specular
    a, b = 0.67, 0.72
    shading = (diffuse * a + detail * (1 - a)) * b + specular * (1 - b)

    # make a high contrast and low contrast version
    high_relief = skimage.exposure.adjust_sigmoid(
        shading, cutoff=high_relief_cutoff, gain=high_relief_gain)

    low_relief = skimage.exposure.adjust_sigmoid(
        shading, cutoff=low_relief_cutoff, gain=low_relief_gain)

    # height field as mask
    height_mask = skimage.exposure.rescale_intensity(
        elevation, in_range=height_mask_range)

    height_mask = 1.0 - skimage.exposure.adjust_gamma(
        height_mask, height_mask_gamma)

    # blend different contrast together using heightfield mask
    shading = low_relief * height_mask + (1. - height_mask) * high_relief

    return shading


#
# Shaded relief
#

class ShadedRelief(ImageryLayer):
    PROTOTYPE = 'shadedrelief'

    def __init__(self, name,
                 index,
                 buffer=16,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=45,
                 **args
                 ):
        ImageryLayer.__init__(self, name)

        if callable(index):
            self._source_index = index
        else:
            self._source_index = lambda x, y: index

        if callable(zfactor):
            self._zfactor = zfactor
        else:
            self._zfactor = lambda x, y: zfactor

        self._scale = scale
        self._azimuth = azimuth
        self._altitude = altitude
        self._buffer = buffer

        self._renderer_parameters = args

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
        source_index = self._source_index(res_x, res_y)

        source = RasterDataSource(source_index)

        elevation = source.query(context.map_proj, envelope,
                                 envelope_size, bands=[1])[0]

        # calculate shaded relief
        zfactor = self._zfactor(res_x, res_y)
        relief = swiss_shaded_relief(elevation,
                                     (res_x, res_y),
                                     scale=self._scale,
                                     z_factor=zfactor,
                                     azimuth=self._azimuth,
                                     altitude=self._altitude,
                                     **self._renderer_parameters)

        # convert to image feature
        relief_image = array2pillow(relief, width, height, self._buffer)
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
        result = result[self._buffer:width + self._buffer,
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
