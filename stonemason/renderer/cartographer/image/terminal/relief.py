# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.terminal.relief
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of shaded relief render node.
"""
__author__ = 'ray'
__date__ = '6/17/15'

import math
import logging
import numpy as np
import skimage
import skimage.exposure
from PIL import Image, ImageOps
from scipy import ndimage
from osgeo import gdal, osr, gdalconst
from stonemason.pyramid.geo import Envelope
from stonemason.renderer.engine.rendernode import TermNode
from stonemason.renderer.engine.context import RenderContext
from stonemason.storage.featurestorage import create_feature_storage
from ..feature import ImageFeature

__all__ = ['SimpleRelief', 'SwissRelief', 'ColorRelief']


#
# Helper functions
#

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


class ReliefNodeImpl(TermNode):
    def __init__(self, name,
                 domain,
                 postprocessor,
                 render_parameters,
                 datasource,
                 rasterizer,
                 buffer):
        assert isinstance(render_parameters, dict)
        TermNode.__init__(self, name)

        self._render_parameters = dict(
            (k, Parameter(v)) for k, v in render_parameters.items())
        self._connection_string = Parameter(datasource)

        self._domain = domain

        self._postprocessor = postprocessor
        self._rasterizer = rasterizer

        self._buffer = buffer
        self._storage_cache = dict()

    def _create_storage(self, resolution):
        connection_string = self._connection_string(resolution)

        if connection_string in self._storage_cache:
            storage = self._storage_cache[connection_string]
        else:
            storage = create_feature_storage(connection_string)
            self._storage_cache[connection_string] = storage

        return storage

    def _create_postprocessor(self, resolution):
        render_parameters = dict(
            (k, v(resolution)) for k, v in self._render_parameters.items())
        return self._postprocessor(resolution, **render_parameters)

    def _create_rasterizer(self, resolution):
        return self._rasterizer(self._buffer)

    def _mosaic(self, crs, envelope, size, storage):

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
            if not target_crs.IsSame(storage.crs):
                ctl_envelope_geom.TransformTo(storage.crs)
            ctl_envelope = Envelope.from_ogr(ctl_envelope_geom.GetEnvelope())
            ctl_transform = GeoTransform.from_envelope(ctl_envelope, size)

            # retrieve source data
            for raster_key in storage.intersection(ctl_envelope):
                logging.debug('Reading: %s' % raster_key)

                source = storage.get(raster_key)
                if source is None:
                    continue

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

    def render(self, context):
        assert isinstance(context, RenderContext)
        crs = context.map_proj
        envelope = context.map_bbox
        size = context.map_size
        resolution = _calc_resolution(envelope, size)

        buffer_envelope = _buffer_envelope(envelope, resolution, self._buffer)
        buffer_envelope_size = _buffer_size(size, self._buffer)

        storage = self._create_storage(resolution)
        array = self._mosaic(crs=crs, envelope=buffer_envelope,
                             size=buffer_envelope_size, storage=storage)

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

    def __init__(self, name, datasource,
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


        ReliefNodeImpl.__init__(self, name,
                                domain=ElevationDataDomain(),
                                postprocessor=SimpleReliefProcessor,
                                render_parameters=render_parameters,
                                datasource=datasource,
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

    def __init__(self, name, datasource,
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

        ReliefNodeImpl.__init__(self, name,
                                domain=ElevationDataDomain(),
                                postprocessor=SwissReliefProcessor,
                                render_parameters=render_parameters,
                                datasource=datasource,
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

    def __init__(self, name, datasource, buffer=0):
        render_parameters = dict()

        ReliefNodeImpl.__init__(self, name,
                                domain=RGBDataDomain(),
                                postprocessor=ColorReliefProcessor,
                                render_parameters=render_parameters,
                                datasource=datasource,
                                rasterizer=RGBRasterizer,
                                buffer=buffer)
