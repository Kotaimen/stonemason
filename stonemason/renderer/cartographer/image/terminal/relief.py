# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.terminal.relief
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of shaded relief render node.
"""
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

from stonemason.renderer.engine.rendernode import TermNode
from stonemason.renderer.engine.context import RenderContext
from stonemason.storage.featurestorage.raster import create_raster_storage

from ..feature import ImageFeature

__all__ = ['SimpleRelief', 'SwissRelief', 'ColorRelief']


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


def hill_shading(aspect, slope, azimuth=315., altitude=45.):
    """Generate hill shading map from aspect and slope, which are the result of
    :func:`~stonemason.renderer.cartographer.image.relief.aspect_and_slope`.

    :return: Generated shaded relief.
    :rtype: numpy.array
    """
    zenith = math.radians(90. - float(altitude) % 360.)
    azimuth = math.radians(float(azimuth))

    shade = ((math.cos(zenith) * np.cos(slope)) +
             (math.sin(zenith) * np.sin(slope) * np.cos(azimuth - aspect)))

    shade[shade < 0] = 0.
    return shade


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
                        blend=(0.65, 0.75),
                        high_relief_cutoff=0.6,
                        high_relief_gain=5,
                        low_relief_cutoff=0.72,
                        low_relief_gain=2,
                        height_mask_range=(0, 3000),
                        height_mask_gamma=0.5,
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
        comes from top, ``0`` is raking light, default value is ``(45, 50, 80)``.
    :type altitude: tuple

    :param blend: Blend opacity of hillshading.
    :type blend: tuple

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

    aspect, slope = aspect_and_slope(elevation, resolution,
                                     scale=scale,
                                     z_factor=z_factor)

    # Use different lighting angle to calculate different exposures:
    #   diffuse = hill_shading(aspect, slope, azimuth, z1)
    #   detail = hill_shading(aspect, slope, azimuth - 180, z2)
    #   specular = hill_shading(aspect, slope, azimuth, z3)
    # Toning by blend different exposures together:
    #    diffuse <-p- detail <-q- specular

    assert azimuth > 180
    zenith = lambda a: math.radians(90. - float(a) % 360.)
    z1, z2, z3 = tuple(map(zenith, altitude))
    azimuth = math.radians(float(azimuth))
    p, q = blend

    shading = np.cos(slope) * \
              (p * q * np.cos(z1) - (-1 + p) * q * np.cos(z2) -
               (-1 + q) * np.cos(z3)) + \
              np.cos(aspect - azimuth) * np.sin(slope) * \
              (p * q * np.sin(z1) + (-1 + p) * q * np.sin(z2) -
               (-1 + q) * np.sin(z3))
    shading[shading < 0] = 0.

    # height field as mask
    height_mask = skimage.exposure.rescale_intensity(elevation,
                                                     in_range=height_mask_range)
    # apply gamma
    height_mask **= height_mask_gamma

    # blend different contrast together using heightfield mask
    c1, c2 = high_relief_cutoff, low_relief_cutoff
    g1, g2 = high_relief_gain, low_relief_gain

    shading = height_mask / (1 + np.exp((-shading + c1) * g1)) \
              + (1 - height_mask) / (1 + np.exp((-shading + c2) * g2))

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


class PostProcessor(object):
    def __call__(self, array):
        raise NotImplementedError


class SimpleReliefProcessor(PostProcessor):
    def __init__(self, resolution, **params):
        self._resolution = resolution
        self._params = params

    def __call__(self, array):
        array = array[0]
        relief = simple_shaded_relief(
            array, self._resolution, **self._params)
        return relief


class SwissReliefProcessor(PostProcessor):
    def __init__(self, resolution, **params):
        self._resolution = resolution
        self._params = params

    def __call__(self, array):
        array = array[0]
        relief = swiss_shaded_relief(
            array, self._resolution, **self._params)
        return relief


class ColorReliefProcessor(PostProcessor):
    def __init__(self, resolution, **params):
        self._resolution = resolution
        self._params = params

    def __call__(self, array):
        rgb_array = np.dstack(array).astype(np.ubyte)
        return rgb_array


class Rasterizer(object):
    def __call__(self, array):
        raise NotImplementedError


class GrayScaleRasterizer(Rasterizer):
    def __init__(self, buffer=0):
        self._buffer = buffer

    def __call__(self, array):
        assert len(array.shape) == 2
        image_array = skimage.img_as_ubyte(array)

        image = Image.fromarray(image_array, mode='L')
        image = ImageOps.crop(image, self._buffer)

        image = image.convert('RGBA')

        return image


class RGBRasterizer(Rasterizer):
    def __init__(self, buffer=0):
        self._buffer = buffer

    def __call__(self, array):
        assert len(array.shape) == 3 and array.shape[2] == 3
        image_array = skimage.img_as_ubyte(array)

        image = Image.fromarray(image_array, 'RGB')
        image = ImageOps.crop(image, self._buffer)

        image = image.convert('RGBA')

        return image


class ReliefNodeImpl(TermNode):
    def __init__(self, name,
                 postprocessor,
                 render_parameters,
                 storage_parameters,
                 rasterizer,
                 buffer):
        assert isinstance(render_parameters, dict)
        assert isinstance(storage_parameters, dict)
        TermNode.__init__(self, name)

        self._render_parameters = dict(
            (k, Parameter(v)) for k, v in render_parameters.items())
        self._storage_parameters = dict(
            (k, Parameter(v)) for k, v in storage_parameters.items())

        self._postprocessor = postprocessor
        self._rasterizer = rasterizer

        self._buffer = buffer
        self._storage_cache = dict()

    def _create_storage(self, resolution):
        storage_parameters = dict(
            (k, v(resolution)) for k, v in self._storage_parameters.items())

        hash = tuple(sorted(storage_parameters.items()))
        if hash in self._storage_cache:
            storage = self._storage_cache[hash]
        else:
            storage = create_raster_storage(**storage_parameters)
            self._storage_cache[hash] = storage

        return storage

    def _create_postprocessor(self, resolution):
        render_parameters = dict(
            (k, v(resolution)) for k, v in self._render_parameters.items())
        return self._postprocessor(resolution, **render_parameters)

    def _create_rasterizer(self, resolution):
        return self._rasterizer(self._buffer)

    def render(self, context):
        assert isinstance(context, RenderContext)
        crs = context.map_proj
        envelope = context.map_bbox
        size = context.map_size
        resolution = _calc_resolution(envelope, size)

        buffer_envelope = _buffer_envelope(envelope, resolution, self._buffer)
        buffer_envelope_size = _buffer_size(size, self._buffer)

        storage = self._create_storage(resolution)
        array = storage.intersection(
            buffer_envelope, crs=crs, size=buffer_envelope_size)

        postprocessor = self._create_postprocessor(resolution)
        array = postprocessor(array)

        rasterizer = self._create_rasterizer(resolution)
        image = rasterizer(array)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=image)

        return feature


class SimpleRelief(ReliefNodeImpl):
    """Simple Shaded Relief Render Node

    `SimpleRelief` produces shaded relief in a simple fast way. Hill shade is
    generated from aspect and slope calculated from raster elevation data,

    **Formulas**:

    1. Calculate aspect and slope:

        .. math::

            \\begin{align}
            slope\_radians& = \\arctan (z\_factor \\div scale \\times \\sqrt{ ( \\frac{\\mathrm{d} z}{\\mathrm{d} x} )^2 + ( \\frac{\\mathrm{d} z}{\\mathrm{d} y} )^2 } ) \\\\
            aspect\_radians& = \\frac{\pi}{2} - \\arctan2 ( \\frac{\\mathrm{d} z}{\\mathrm{d} y}, -\\frac{\\mathrm{d} z}{\\mathrm{d} x} )
            \\end{align}

    2. Calculate hillshade:

        .. math::

            \\begin{equation}
            \\begin{split}
            hillshade &= 1.0 \\times ((\\cos(zenith\_rad) \\times \\cos(slope\_rad))\\\\
                      & \quad + sin(zenith\_rad) \\times \\sin(slope\_rad) \\times \\cos(azimuth\_rad - aspect\_rad))
            \\end{split}
            \\end{equation}

    For detail, please see `How Hillshade works`_.

    .. _How Hillshade works: http://help.arcgis.com/EN/arcgisdesktop/10.0/help/index.html#/How_Hillshade_works/009z000000z2000000/


    :param name: a string literal that identifies the node
    :type name: str

    :param index: pathname of raster index file.
    :type index: str

    :param z_factor: Vertical exaggeration used to pre-multiply the elevations,
        default value is ``1``, which means no exaggeration.
    :type z_factor: float

    :param scale: Ratio of vertical units to horizontal. If the horizontal
        unit of the elevation raster is degrees (e.g: ``WGS84``), set `scale`
        to ``111120`` if the vertical unit is meter, or set to ``370400``
        if vertical unit is feet.
    :type scale: float

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

    :param buffer: extra pixels added to ensure continuity of rendered feature.
    :type buffer: int

    :return: Rendered shaded relief as a image.
    :rtype: numpy.array

    """

    def __init__(self, name, raster_storage,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=45,
                 cutoff=0.707,
                 gain=4,
                 buffer=0):
        render_parameters = dict(z_factor=zfactor,
                                 scale=scale,
                                 azimuth=azimuth,
                                 altitude=altitude,
                                 cutoff=cutoff,
                                 gain=gain)

        assert 'prototype' in raster_storage
        if raster_storage['prototype'] not in ['elevation.s3', 'elevation.disk']:
            raise ValueError('Swiss Relief should have a Elevation source!')

        storage_parameters = raster_storage

        ReliefNodeImpl.__init__(self, name,
                                postprocessor=SimpleReliefProcessor,
                                render_parameters=render_parameters,
                                storage_parameters=storage_parameters,
                                rasterizer=GrayScaleRasterizer,
                                buffer=buffer)


class SwissRelief(ReliefNodeImpl):
    """Swiss Relief Render Node

    Maps with coloured relief shading, modulated by elevation and by exposure
    to illumination, present topography in a particularly vivid and descriptive
    manner, helping map-readers to conceive more easily the terrain’s important
    landforms.

    `SwissRelief` produces shaded relief in a more complex way comparing with
    the `SimpleRelief`. It introduces a new contemporary digital procedure to
    mimic the style used on Swiss topographic maps developed by `Eduard Imhof`_,
    a professor of cartography and artist. One of Imhof’s most important
    contributions was the development of a photomechanical process for the
    production of coloured shaded relief (around 1945).

    .. _Eduard Imhof: https://en.wikipedia.org/wiki/Eduard_Imhof



    Illumination Model:

        The illumination model of `SwissRelief` combines shaded reliefs
        illuminated by three different light angles and intensities to
        provide a simulated effect of global illumination.

        This approach avoids “dead” mountain ridges in transition zones,
        emphasizing and clarifying important topographic features, such as
        ridges, valleys and watersheds.

    Aerial Perspective:

        The aerial perspective effect is an essential design component of
        traditional shaded relief, which is based on natural observation.
        The concept is familiar to anyone who has hiked up a mountain--the
        veiling effects of atmospheric haze cause topographic features in
        the distance to look fainter than features in the foreground.

        When aerial perspective is applied to map shaded relief, higher
        topographic features should be shown with slightly more contrast
        than lowland features because they appear closer to readers who,
        theoretically, view the map from above.

        For more detail, please refer to `Creating Swiss-style shaded relief in Photoshop`_.

        .. _Creating Swiss-style shaded relief in Photoshop: http://www.shadedrelief.com/shading/Swiss.html

    :param name: a string literal that identifies the node
    :type name: str

    :param index: pathname of raster index file.
    :type index: str

    :param z_factor: Vertical exaggeration used to pre-multiply the elevations,
        default value is ``1``, which means no exaggeration.
    :type z_factor: float

    :param scale: Ratio of vertical units to horizontal. If the horizontal
        unit of the elevation raster is degrees (e.g: ``WGS84``), set `scale`
        to ``111120`` if the vertical unit is meter, or set to ``370400``
        if vertical unit is feet.
    :type scale: float

    :param azimuth: Azimuth of the light, in degrees.  ``0`` comes from north,
        ``90`` from the east... default value is ``315``.
    :type azimuth: float

    :param altitude: a list of altitude of the light, in degrees. ``90`` if the light
        comes from top, ``0`` is raking light, default value is ``45``
    :type altitude: list

    :param high_relief_cutoff: `Cutoff` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``0.6``. Used by
        high altitude relief.
    :type high_relief_cutoff: float

    :param high_relief_gain: `Gain` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``5``. Used by
        high altitude relief.
    :type gain: float

    :param low_relief_cutoff: `Cutoff` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``0.72``. Used by
        high altitude relief.
    :type high_relief_cutoff: float

    :param low_relief_gain: `Gain` parameter of the sigmoid contrast function, see
        :func:`skimage.exposure.adjust_sigmoid`, default value is ``2``. Used by
        low altitude relief.
    :type gain: float

    :param height_mask_range: A ``(min, max)`` tuple that mask the lowland range,
        default value is ``(0, 3000)``.
    :type height_mask_range: tuple

    :param height_mask_gamma: gamma correction applied on the height mask, default
        value is 0.5.
    :type height_mask_gamma: float

    :param blend: two weight values for composing diffuse, detail and specular hillshades.
    :type blend: tuple

    :param buffer: extra pixels added to ensure continuity of rendered feature.
    :type buffer: int

    """

    def __init__(self, name, raster_storage,
                 zfactor=1,
                 scale=111120,
                 azimuth=315,
                 altitude=(45, 50, 80),
                 high_relief_cutoff=0.6,
                 high_relief_gain=5,
                 low_relief_cutoff=0.72,
                 low_relief_gain=2,
                 height_mask_range=(0, 3000),
                 height_mask_gamma=0.5,
                 blend=(0.65, 0.75),
                 buffer=0):
        render_parameters = dict(z_factor=zfactor,
                                 scale=scale,
                                 azimuth=azimuth,
                                 altitude=altitude,
                                 high_relief_cutoff=high_relief_cutoff,
                                 high_relief_gain=high_relief_gain,
                                 low_relief_cutoff=low_relief_cutoff,
                                 low_relief_gain=low_relief_gain,
                                 height_mask_range=height_mask_range,
                                 height_mask_gamma=height_mask_gamma,
                                 blend=blend)

        assert 'prototype' in raster_storage
        if raster_storage['prototype'] not in ['elevation.s3', 'elevation.disk']:
            raise ValueError('Swiss Relief should have a Elevation source!')

        storage_parameters = raster_storage

        ReliefNodeImpl.__init__(self, name,
                                postprocessor=SwissReliefProcessor,
                                render_parameters=render_parameters,
                                storage_parameters=storage_parameters,
                                rasterizer=GrayScaleRasterizer,
                                buffer=buffer)


class ColorRelief(ReliefNodeImpl):
    """Image Raster Render Node

    The `ColorRelief` render node renders raster data set with RGB bands.

    :param name: a string literal that identifies the node
    :type name: str

    :param index: pathname of raster index file.
    :type index: str

    :param buffer: extra pixels added to ensure continuity of rendered feature.
    :type buffer: int

    """

    def __init__(self, name, raster_storage, buffer=0):
        render_parameters = dict()

        storage_parameters = raster_storage

        assert 'prototype' in raster_storage
        if raster_storage['prototype'] not in ['rgb.s3', 'rgb.disk']:
            raise ValueError('Color Relief should have a RGB source!')

        ReliefNodeImpl.__init__(self, name,
                                postprocessor=ColorReliefProcessor,
                                render_parameters=render_parameters,
                                storage_parameters=storage_parameters,
                                rasterizer=RGBRasterizer,
                                buffer=buffer)
