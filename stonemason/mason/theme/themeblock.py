# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.themeblock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Blocks of a stonemason theme.

"""

import re
import six
import json


class ThemeBlockError(Exception):
    """Theme Block Error Base Class
    """
    pass


class MetadataValueError(ThemeBlockError):
    """Invalid metadata value
    """
    pass


class ModeValueError(ThemeBlockError):
    """Invalid mode value
    """


class ThemeBlock(object):
    """Theme Block Base Class
    """
    pass


class MetadataBlock(ThemeBlock):
    """Theme Metadata

    The MetadataBlock contains metadata of a stonemason theme. It is a
    namedtuple with additional functions.

    For python2, namedtuple._replace should not be used because it will bypass
    the validation check defined the new

    The following metadata is required:

    `name`

        A string literal that uniquely identify a theme. Different theme
        should have different names. The default value is 'default'.


    `crs`

        A coordinate reference system(CRS) defines a specific map projection,
        as well as transformations between different spatial reference systems.
        Validation is delayed to backend. The default value is 'epsg:3857'.


    `scale`

        A positive integer number which scales, or multiplies element size
        throughout the map rendering process for display on high resolution
        device. If you are rendering maps for a retina display, you should
        probably use scale 2.
        Range [1, 5). The default value is 1.


    `buffer`

        The padding space on all sides of a `metatile`. It will be
        multiplied by the `scale` factor. The default value is 0.


    `stride`

        The number of steps along the axis of a `metatile` grid. It must be a
        positive integer powers of 2. For a 2x2 metatile, the stride is 2.
        The default value is 1.


    `format`

        Output format. The default value is 'png'.


    `format_options`

        Options of Output format.


    `attribution`

        Description about authors or copyright information.


    :param name: Theme name.
    :type name: str
    :param crs: A coordinate reference system(CRS).
    :type crs: str
    :param scale: A proportional scale ratio.
    :type scale: int
    :param buffer: Extra boundary area size in pixels.
    :type buffer: int
    :param stride: The number of steps along a axis of a metatile grid.
    :type stride: int
    :param format: Output format.
    :type format: str
    :param format_options: Output format options.
    :type format_options: dict
    :param attribution: Information about authors or copyright.
    :type attribution: str
    """

    def __init__(self,
                 name='default',
                 crs='epsg:3857',
                 scale=1,
                 buffer=0,
                 stride=1,
                 format='png',
                 format_options=None,
                 attribution=''):
        if not isinstance(name, six.string_types) \
                or not re.match('^[a-zA-Z]+[a-zA-Z0-9]*$', name):
            raise MetadataValueError(
                'Name should be a string literal with ONLY ascii alpha '
                'characters!')

        if not isinstance(crs, six.string_types):
            raise MetadataValueError(
                'CRS could be a projection string, a spatial reference system '
                'identifier(SRID), or a conventional name(WGS84)!')

        if not isinstance(scale, int) or scale < 1 or scale >= 5:
            raise MetadataValueError(
                'A positive integer (1-5) is required.')

        if not isinstance(buffer, int) or buffer < 0:
            raise MetadataValueError(
                'Zero or a positive integer.')

        # check if stride is power of 2
        if not isinstance(stride, int) \
                or ((stride & (stride - 1)) != 0) or stride <= 0:
            raise MetadataValueError(
                'A positive integer powers of 2 is required!')

        if not isinstance(format, six.string_types) \
                or format not in ('png', 'jpeg', 'geojson'):
            raise MetadataValueError(
                'Available Output format includes raster format like png, jpeg '
                'or vector format geojson.')

        if format_options and not isinstance(format_options, dict):
            raise MetadataValueError(
                'A dict object of parameters of the format is required.')

        if not isinstance(attribution, six.string_types):
            raise MetadataValueError(
                'Attribution Should be a string literal.')

        self._metadata = dict(
            name=name,
            crs=crs,
            scale=scale,
            buffer=buffer,
            stride=stride,
            format=format,
            format_options=format_options,
            attribution=attribution,
        )

    @property
    def name(self):
        return self._metadata['name']

    @property
    def crs(self):
        return self._metadata['crs']

    @property
    def scale(self):
        return self._metadata['scale']

    @property
    def buffer(self):
        return self._metadata['buffer'] * self._metadata['scale']

    @property
    def stride(self):
        return self._metadata['stride']

    @property
    def format(self):
        return self._metadata['format']

    @property
    def format_options(self):
        return self._metadata['format_options']

    @property
    def attribution(self):
        return self._metadata['attribution']

    @property
    def tag(self):
        suffix = ''
        if self.scale > 1:
            suffix = '@%dx' % self.scale

        tag = self.name + suffix

        return tag

    def to_json(self):
        return json.dumps(self._metadata)

    def __repr__(self):
        return "MetadataBlock(name=%(name)r, crs=%(crs)r, " \
               "scale=%(scale)r, buffer=%(buffer)r, stride=%(stride)r, " \
               "format=%(format)r, format_options=%(format_options)r, " \
               "attribution=%(attribution)r)" % self._metadata


class ModeBlock(ThemeBlock):
    """Theme Mode

    Controls the running mode of a provider .

    `mode`

        The following modes are supported now:

        ``
    """

    def __init__(self, mode):
        if not isinstance(mode, six.string_types) \
                or mode not in ('storage-only', 'hybrid'):
            raise ModeValueError('Only support "storage-only", "hybrid" mode!')

        self._mode = mode

    @property
    def mode(self):
        return self._mode


class CacheBlock(ThemeBlock):
    pass


class StorageBlock(ThemeBlock):
    pass


class DesignBlock(ThemeBlock):
    pass
