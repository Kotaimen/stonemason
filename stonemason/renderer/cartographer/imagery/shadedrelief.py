# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/15'

import math

import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

import skimage
import skimage.exposure
import skimage.filters
import skimage.segmentation
import skimage.morphology

from stonemason.renderer.layerexpr import ImageryLayer
from stonemason.renderer.feature import ImageFeature
from stonemason.renderer.context import RenderContext

from .datasource import ElevationDataSource, RGBImageDataSource


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
                        z_factor=1., azimuth=315,
                        altitude=(45, 50, 80),
                        high_relief_cutoff=0.6,
                        high_relief_gain=5,
                        low_relief_cutoff=0.72,
                        low_relief_gain=2,
                        height_mask_range=(0, 3000),
                        height_mask_gamma=0.5,
                        blend=(0.65, 0.75),
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
    a1, a2, a3 = altitude
    diffuse = hill_shading(aspect, slope, azimuth, a1)
    detail = hill_shading(aspect, slope, azimuth - 180, a2)
    specular = hill_shading(aspect, slope, azimuth, a3)

    # toning by blend different exposures together:
    #    diffuse <-a- detail <-b- specular
    a, b = blend
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


def _calc_resolution(envelope, size):
    left, bottom, right, top = envelope
    width, height = size

    # calculate map resolution
    res_x = (right - left) / width
    res_y = (top - bottom) / height

    return res_x, res_y


def _buffer_envelope(envelope, resolution, buffer):
    left, bottom, right, top = envelope
    res_x, res_y = resolution

    # calculate buffered envelope size
    buffer_x = res_x * buffer
    buffer_y = res_y * buffer

    # calculate buffered map envelope
    envelope = (left - buffer_x, bottom - buffer_y,
                right + buffer_x, top + buffer_y)
    return envelope


def _buffer_size(size, buffer):
    width, height = size
    size = width + 2 * buffer, height + 2 * buffer
    return size


class Parameter(object):
    def __init__(self, value=None):
        self._value = value

    def __call__(self, resolution):
        if callable(self._value):
            return self._value(resolution)
        else:
            return self._value


class SimpleRelief(ImageryLayer):
    PROTOTYPE = 'relief.simple'

    def __init__(self, name, index,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=45,
                 cutoff=0.707,
                 gain=4,
                 buffer=0):
        ImageryLayer.__init__(self, name)

        self._index = Parameter(index)

        self._zfactor = Parameter(zfactor)
        self._scale = Parameter(scale)
        self._azimuth = Parameter(azimuth)
        self._altitude = Parameter(altitude)
        self._cutoff = Parameter(cutoff)
        self._gain = Parameter(gain)

        self._buffer = buffer

    def render(self, context):
        assert isinstance(context, RenderContext)
        crs = context.map_proj
        envelope = context.map_bbox
        size = context.map_size

        resolution = _calc_resolution(envelope, size)

        buffered_envelope = _buffer_envelope(envelope, resolution, self._buffer)
        buffered_envelope_size = _buffer_size(size, self._buffer)

        with ElevationDataSource(self._index(resolution)) as source:
            elevation = source.query(
                crs, buffered_envelope, buffered_envelope_size)[0]

            zfactor = self._zfactor(resolution)
            scale = self._scale(resolution)
            azimuth = self._azimuth(resolution)
            altitude = self._altitude(resolution)
            cutoff = self._cutoff(resolution)
            gain = self._gain(resolution)

            relief = simple_shaded_relief(elevation,
                                          resolution,
                                          scale=scale,
                                          z_factor=zfactor,
                                          azimuth=azimuth,
                                          altitude=altitude,
                                          cutoff=cutoff,
                                          gain=gain)

            image = skimage.img_as_ubyte(relief)

            pil_image = Image.fromarray(image, mode='L')
            pil_image = ImageOps.crop(pil_image, self._buffer)

            feature = ImageFeature(crs=context.map_proj,
                                   bounds=context.map_bbox,
                                   size=context.map_size,
                                   data=pil_image)

            return feature


class SwissRelief(ImageryLayer):
    PROTOTYPE = 'relief.swiss'

    def __init__(self, name, index,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=45,
                 high_relief_cutoff=0.7,
                 high_relief_gain=5,
                 low_relief_cutoff=0.7,
                 low_relief_gain=1,
                 height_mask_range=(0, 3000),
                 height_mask_gamma=0.5,
                 buffer=0):
        ImageryLayer.__init__(self, name)

        self._index = Parameter(index)

        self._zfactor = Parameter(zfactor)
        self._scale = Parameter(scale)
        self._azimuth = Parameter(azimuth)
        self._altitude = Parameter(altitude)
        self._high_relief_cutoff = Parameter(high_relief_cutoff)
        self._high_relief_gain = Parameter(high_relief_gain)
        self._low_relief_cutoff = Parameter(low_relief_cutoff)
        self._low_relief_gain = Parameter(low_relief_gain)
        self._height_mask_range = Parameter(height_mask_range)
        self._height_mask_gamma = Parameter(height_mask_gamma)

        self._buffer = buffer

    def render(self, context):
        assert isinstance(context, RenderContext)
        crs = context.map_proj
        envelope = context.map_bbox
        size = context.map_size

        resolution = _calc_resolution(envelope, size)

        buffered_envelope = _buffer_envelope(envelope, resolution, self._buffer)
        buffered_envelope_size = _buffer_size(size, self._buffer)

        with ElevationDataSource(self._index(resolution)) as source:
            elevation = source.query(
                crs, buffered_envelope, buffered_envelope_size)[0]

            zfactor = self._zfactor(resolution)
            scale = self._scale(resolution)
            azimuth = self._azimuth(resolution)
            altitude = self._altitude(resolution)
            high_relief_cutoff = self._high_relief_cutoff(resolution)
            high_relief_gain = self._high_relief_gain(resolution)
            low_relief_cutoff = self._low_relief_cutoff(resolution)
            low_relief_gain = self._low_relief_gain(resolution)
            height_mask_range = self._height_mask_range(resolution)
            height_mask_gamma = self._height_mask_gamma(resolution)

            relief = swiss_shaded_relief(elevation,
                                         resolution,
                                         scale=scale,
                                         z_factor=zfactor,
                                         azimuth=azimuth,
                                         altitude=altitude,
                                         high_relief_cutoff=high_relief_cutoff,
                                         low_relief_cutoff=low_relief_cutoff,
                                         high_relief_gain=high_relief_gain,
                                         low_relief_gain=low_relief_gain,
                                         height_mask_range=height_mask_range,
                                         height_mask_gamma=height_mask_gamma)

            image = skimage.img_as_ubyte(relief)

            pil_image = Image.fromarray(image, mode='L')
            pil_image = ImageOps.crop(pil_image, self._buffer)

            feature = ImageFeature(crs=context.map_proj,
                                   bounds=context.map_bbox,
                                   size=context.map_size,
                                   data=pil_image)

            return feature


class ColorRelief(ImageryLayer):
    PROTOTYPE = 'relief.color'

    def __init__(self, name, index, buffer=0):
        ImageryLayer.__init__(self, name)

        self._index = Parameter(index)
        self._buffer = buffer

    def render(self, context):
        assert isinstance(context, RenderContext)
        crs = context.map_proj
        envelope = context.map_bbox
        size = context.map_size

        resolution = _calc_resolution(envelope, size)

        buffered_envelope = _buffer_envelope(envelope, resolution, self._buffer)
        buffered_envelope_size = _buffer_size(size, self._buffer)

        with RGBImageDataSource(self._index(resolution)) as source:
            channels = source.query(
                crs, buffered_envelope, buffered_envelope_size)

            rgb_array = np.dstack(channels).astype(np.ubyte)

            pil_image = Image.fromarray(rgb_array, 'RGB')
            pil_image = pil_image.convert('RGBA')

            pil_image = ImageOps.crop(pil_image, self._buffer)

            feature = ImageFeature(crs=context.map_proj,
                                   bounds=context.map_bbox,
                                   size=context.map_size,
                                   data=pil_image)

            return feature
