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


def is_integer(val):
    return isinstance(val, int)


def is_integer_in_range(val, start, end):
    return isinstance(val, int) and val in range(start, end)


def is_powers_of_2(val):
    return ((val & (val - 1)) == 0) and val > 0


def is_string(val):
    return isinstance(val, six.string_types)


def is_list(val):
    return isinstance(val, list)


def is_dict(val):
    return isinstance(val, dict)


class MetadataBlock(ThemeBlock):
    """Theme Metadata

    The `MetadataBlock` contains setup information of a stonemason theme.

    The following settings are available:

    `name`

        A string literal that uniquely identify a theme. Different theme
        should have different names. The default value is `default`.


    `crs`

        A coordinate reference system(CRS) defines a specific map projection,
        as well as transformations between different spatial reference systems.
        Validation is delayed to backend. The default value is `EPSG:3857`.


    `scale`

        A positive integer number which scales, or multiplies element size
        throughout the map rendering process for display on high resolution
        device. If you are rendering maps for a retina display, you should
        probably use scale 2.
        Valid value ranges from 1 to 4. The default value is 1.


    `buffer`

        The padding space on all sides of a `metatile`. It will be
        multiplied by the `scale` factor. The default value is 0.


    `stride`

        The number of steps along the axis of a `metatile` grid. It must be a
        positive integer powers of 2. For a 2x2 metatile, the stride is 2.
        The default value is 1.


    `format`

        Output format. The default value is `png`.


    `format_options`

        Options of Output format. None if no options.


    `attribution`

        Description about authors or copyright information.


    :param name: Theme name.
    :type name: str
    :param crs: A coordinate reference system(CRS).
    :type crs: str
    :param scale: A proportional scale ratio.
    :type scale: int or list
    :param buffer: Extra boundary area size in pixels.
    :type buffer: int
    :param stride: The number of steps along a axis of a `metatile` grid.
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
                 crs='EPSG:3857',
                 scale=1,
                 buffer=0,
                 stride=1,
                 format='png',
                 format_options=None,
                 attribution=''):
        if not is_string(name) \
                or not re.match('^[a-zA-Z]+[a-zA-Z0-9]*$', name):
            raise MetadataValueError(
                'Name should be a string literal with ONLY ascii alpha '
                'characters!')

        if not is_string(crs):
            raise MetadataValueError(
                'CRS could be a projection string, a spatial reference system '
                'identifier(SRID), or a conventional name(WGS84)!')

        if is_integer(scale) and is_integer_in_range(scale, 1, 5):
            pass
        elif is_list(scale):
            for s in scale:
                if is_integer(s) and is_integer_in_range(s, 1, 5):
                    pass
        else:
            raise MetadataValueError(
                'A single or a list of positive integers ranging from '
                '1 to 4(included) is required.')

        if not is_integer(buffer) or buffer < 0:
            raise MetadataValueError(
                'Zero or a positive integer.')

        # check if stride is power of 2
        if not is_integer(stride) or not is_powers_of_2(stride):
            raise MetadataValueError(
                'A positive integer powers of 2 is required!')

        if not is_string(format) or format not in ('png', 'jpeg', 'geojson'):
            raise MetadataValueError(
                'Available Output format includes raster format like png, jpeg '
                'or vector format geojson.')

        if format_options and not is_dict(format_options):
            raise MetadataValueError(
                'A dict object of parameters of the format is required.')

        if not is_string(attribution):
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
        """Identifier of the theme"""
        return self._metadata['name']

    @property
    def crs(self):
        """Returns a string represents Coordinate Reference System"""
        return self._metadata['crs']

    @property
    def scale(self):
        """Returns the scale factor"""
        return self._metadata['scale']

    @property
    def buffer(self):
        """Padding size, multiplied by the scale factor"""
        return self._metadata['buffer'] * self._metadata['scale']

    @property
    def stride(self):
        """Stride of a metatile"""
        return self._metadata['stride']

    @property
    def format(self):
        """Output format"""
        return self._metadata['format']

    @property
    def format_options(self):
        """Output format options"""
        return self._metadata['format_options']

    @property
    def attribution(self):
        """Copyright and Author information"""
        return self._metadata['attribution']


    def to_json(self):
        """Returns a json string contains all metadata"""
        return json.dumps(self._metadata)

    def __repr__(self):
        """Returns a repr string"""
        return "MetadataBlock(name=%(name)r, crs=%(crs)r, " \
               "scale=%(scale)r, buffer=%(buffer)r, stride=%(stride)r, " \
               "format=%(format)r, format_options=%(format_options)r, " \
               "attribution=%(attribution)r)" % self._metadata


class CacheBlock(ThemeBlock):
    pass


class StorageBlock(ThemeBlock):
    pass


class ModeBlock(ThemeBlock):
    """Theme Mode

    Controls the running behaviors of a `Provider`.

    `mode`

        The following modes are supported now:

        - storage-only

        Read tile only from the `TileStorage` attached to theme.

        - hybrid

        Read tile from the `TileStorage` and cache them in `TileCache`.

    """

    MODE_STORAGE_ONLY = 'storage-only'

    MODE_HYBRID = 'hybrid'


    def __init__(self, mode):
        if not isinstance(mode, six.string_types) \
                or mode not in (self.MODE_STORAGE_ONLY, self.MODE_HYBRID):
            raise ModeValueError('Only support "storage-only", "hybrid" mode!')

        self._mode = mode

    @property
    def mode(self):
        return self._mode


class DesignBlock(ThemeBlock):
    pass
