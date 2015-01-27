# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.themeblock
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Blocks of a stonemason theme.

"""

import six
import json

from .validator import (
    MinValueValidator,
    MaxValueValidator,
    Power2Validator,
    ExprValidator,
    ChoiceValidator
)

from .field import (
    IntegerBlockField,
    StringBlockField,
    ListBlockField,
    DictBlockField,
)


class ThemeBlockError(Exception):
    """Theme Block Error Base Class
    """
    pass


class ThemeBlockTypeError(ThemeBlockError):
    """Raise when `BlockField` type is invalid.
    """
    pass


class ThemeBlock(object):  # pragma: no cover
    """Theme Block Base Class
    """

    def to_json(self):
        """Dumps into json format"""
        raise NotImplementedError


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

        field_name = StringBlockField('name', name)
        field_name.validate(ExprValidator('^[a-zA-Z]+[a-zA-Z0-9]*$'))

        field_crs = StringBlockField('crs', crs)

        if isinstance(scale, six.integer_types):
            scale = [scale]
        field_scale = ListBlockField('scale', scale)
        field_scale.validate(MinValueValidator(1), MaxValueValidator(4))

        field_buffer = IntegerBlockField('buffer', buffer)
        field_buffer.validate(MinValueValidator(0))

        field_stride = IntegerBlockField('stride', stride)
        field_stride.validate(Power2Validator())

        field_format = StringBlockField('format', format)
        field_format.validate(ChoiceValidator(['png', 'jpeg', 'geojson']))

        if format_options is None:
            format_options = dict()

        field_format_options = DictBlockField('format_options', format_options)

        field_attribution = StringBlockField('attribution', attribution)

        self._metadata = dict(
            name=field_name.value,
            crs=field_crs.value,
            scale=field_scale.value,
            buffer=field_buffer.value,
            stride=field_stride.value,
            format=field_format.value,
            format_options=field_format_options.value,
            attribution=field_attribution.value,
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

    def buffer(self, scale=1):
        """Padding size, multiplied by the scale factor"""
        return self._metadata['buffer'] * scale

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
    """Configurations for `TileCache`

    The `CacheBlock` contains setup information to create a `TileCache` in a
    `Provider`.

    `prototype`

        A string literal represents the type of `TileCache` to create. For now,
        only `memcache` is supported. Default to None.

    `parameters`

        A dict object contains options used to create `TileCache`. Default to
        None. The validation of these option values is delayed to the creation
        of `TileCache`.

    :param prototype: Type of `TileCache`.
    :type prototype: str
    :param parameters: Options used to create `TileCache`.
    :type parameters: dict

    """

    def __init__(self, prototype, parameters):
        field_prototype = StringBlockField('prototype', prototype)
        field_prototype.validate(ChoiceValidator(['memcache']))

        field_parameters = DictBlockField('parameters', parameters)

        self._cache = dict(
            prototype=field_prototype.value,
            parameters=field_parameters.value
        )

    @property
    def prototype(self):
        return self._cache['prototype']

    @property
    def parameters(self):
        return self._cache['parameters']

    def to_json(self):
        return json.dumps(self._cache)

    def __repr__(self):
        return "CacheBlock(prototype=%(prototype)r, parameters=%(parameters)r)" % self._cache


class StorageBlock(ThemeBlock):
    """Configurations for `TileStorage`

    The `StorageBlock` contains setup information to create a `TileStorage`
    in a `Provider`.

    `prototype`

        A string literal represents the type of `TileStorage` to create. For
        now, only `clusterstorage` is supported. Default to None.

    `parameters`

        A dict object contains options used to create `TileStorage`. Default to
        None. The validation of these option values is delayed to the creation
        of `TileStorage`.

    :param prototype: Type of `TileStorage`.
    :type prototype: str
    :param parameters: Options used to create `TileStorage`.
    :type parameters: dict

    """

    def __init__(self, prototype, parameters):
        field_prototype = StringBlockField('prototype', prototype)
        field_prototype.validate(ChoiceValidator(['cluster-storage']))

        field_parameters = DictBlockField('parameters', parameters)

        self._storage = dict(
            prototype=field_prototype.value,
            parameters=field_parameters.value
        )

    @property
    def prototype(self):
        return self._storage['prototype']

    @property
    def parameters(self):
        return self._storage['parameters']

    def to_json(self):
        return json.dumps(self._storage)

    def __repr__(self):
        return "StorageBlock(prototype=%(prototype)r, parameters=%(parameters)r)" % self._storage


class ModeBlock(ThemeBlock):
    """Theme Mode

    Controls the running behaviors of a `Provider`.

    `mode`

        The following modes are supported now:

        - storage-only

        Read tile only from the `TileStorage` attached to theme.

        - hybrid

        Read tile from the `TileStorage` and cache them in `TileCache`.

    :param mode: Running behavior of a `Provider`.
    :type mode: str

    """

    MODE_STORAGE_ONLY = 'storage-only'

    MODE_HYBRID = 'hybrid'

    MODES = [MODE_STORAGE_ONLY, MODE_HYBRID]

    def __init__(self, mode=MODE_STORAGE_ONLY):
        field_mode = StringBlockField('mode', mode)
        field_mode.validate(ChoiceValidator(self.MODES))

        self._modes = dict(
            mode=mode
        )

    @property
    def mode(self):
        return self._modes['mode']

    def to_json(self):
        return json.dumps(self._modes)

    def __repr__(self):
        return "ModeBlock(mode=%(mode)r)" % self._modes


class DesignBlock(ThemeBlock):
    pass
