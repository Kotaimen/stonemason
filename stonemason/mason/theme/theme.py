# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme and relative theme elements.

"""

__author__ = 'ray'
__date__ = '2/8/15'

import re

from .element import ThemeElement


class ThemeError(Exception):
    pass


class InvalidThemeValue(ThemeError):
    pass


class ThemeRoot(ThemeElement):
    """Root Theme Element

    The `ThemeRoot` serves as the root of all the theme elements.

    """

    def __init__(self, name, **attributes):
        ThemeElement.__init__(
            self, name, maptype=attributes.get('maptype', 'image'))

    @property
    def maptype(self):
        return self.attributes['maptype']

    def validate(self):
        if not re.match('^[a-zA-Z][a-zA-Z0-9@_]*$', self.name):
            raise InvalidThemeValue(self.name)

        return ThemeElement.validate(self)


class ThemeMetadata(ThemeElement):
    """Metadata Theme Element

    The `ThemeMetadata` is one of the basic building elements of a `Theme`.
    It contains basic properties of a theme. Properties in ThemeMetadata
    aims to provide better understanding of a Theme.

    Samples:

    >>> from stonemason.mason.theme.theme import ThemeMetadata
    >>> m = ThemeMetadata('metadata',
    ...                   version='0.0.1',
    ...                   description='A sample',
    ...                   attribution='Q',
    ...                   thumbnail='http://localhost/thumb.jpg',
    ...                   center=[139, 35],
    ...                   center_zoom=5)
    >>> m.name
    'metadata'
    >>> m.version
    '0.0.1'
    >>> m.description
    'A sample'
    >>> m.attribution
    'Q'
    >>> m.thumbnail
    'http://localhost/thumb.jpg'
    >>> m.center
    [139, 35]
    >>> m.center_zoom
    5

    :param name:

        A string literal represents the name of the `ThemeElement`.

    :type name: str

    :param version:

        A string literal that represents the current edition of the `Theme`.
        For example, ``0.0.1``.

    :type version: str

    :param description:

        A written representation of current `Theme`.

    :type description: str

    :param attribution:

        The statement of the copyright author's identity.

    :type attribution: str

    :param thumbnail:

        A image url that represents the location of a thumbnail.

    :type thumbnail: str

    :param center:

        A [lon, lat] object that represents the initial view point of the
        theme. Default to [0, 0].

    :type center: list

    :param center_zoom:

        A positive integer that represents the initial zoom level of the
        theme. Default to 4.

    :type center_zoom: int

    """

    def __init__(self, name, **attributes):
        ThemeElement.__init__(
            self, name,
            version=attributes.get('version', ''),
            description=attributes.get('description', ''),
            attribution=attributes.get('attribution', 'K&R'),
            thumbnail=attributes.get('thumbnail', ''),
            center=attributes.get('center', [0, 0]),
            center_zoom=attributes.get('center_zoom', 4))

    @property
    def version(self):
        """Current edition of the theme"""
        return self.attributes['version']

    @property
    def description(self):
        """Description of the theme"""
        return self.attributes['description']

    @property
    def attribution(self):
        """Copyright about the theme"""
        return self.attributes['attribution']

    @property
    def thumbnail(self):
        """Thumbnail url"""
        return self.attributes['thumbnail']

    @property
    def center(self):
        """Initial view point of the theme"""
        return self.attributes['center']

    @property
    def center_zoom(self):
        """Initial view level of the theme"""
        return self.attributes['center_zoom']


class ThemePyramid(ThemeElement):
    """Pyramid Theme Element

    The `ThemePyramid` contains properties used to construct a
    :class:`~stonemason.pyramid.Pyramid` tile system.

    Samples:

    >>> from stonemason.mason.theme.theme import ThemePyramid
    >>> p = ThemePyramid('pyramid',
    ...                  levels=range(0, 5),
    ...                  stride=8,
    ...                  geogcs='EPSG:4326',
    ...                  projcs='EPSG:3857')
    >>> p.name
    'pyramid'
    >>> p.levels
    [0, 1, 2, 3, 4]
    >>> p.stride
    8
    >>> p.geogcs
    'EPSG:4326'
    >>> p.projcs
    'EPSG:3857'
    >>> p.geogbounds
    (-180, -85.0511, 180, 85.0511)

    :param name:

        A string literal represents the name of the `ThemeElement`

    :type name: str

    :param levels:

        A list of positive integers indicates available levels for the tile
        system. Default values ranges from 0 to 23 (exclusive).

    :type levels: list

    :param stride:

        A positive integer that represents the number of steps along the side
        of a `metatile`. Its value must be powers of 2. For example, the
        stride of a 2x2 metatile is ``2``. The default value is ``1``.

    :type stride: int

    :param crs:

        A string literal indicates the coordinate reference system(CRS) of the
        data source. The default value is ``EPSG:4326``.

    :type crs: str

    :param proj:

        A string literal that indicates the projection of the tile system. The
        default value is ``EPSG:3857``.

    :type proj: str

    :param boundary:

        A four value tuple indicates the boundary of the tile system. The
        value is specified in coordinate system defined in `crs`. The default
        value is (-180, -85.0511, 180, 85.0511).

    :type boundary: tuple

    """

    def __init__(self, name, **attributes):
        ThemeElement.__init__(
            self, name,
            levels=attributes.get('levels', list(range(0, 23))),
            stride=attributes.get('stride', 1),
            geogcs=attributes.get('geogcs', 'WGS84'),
            projcs=attributes.get('projcs', 'EPSG:3857'),
            geogbounds=attributes.get('geogbounds',
                                      (-180, -85.0511, 180, 85.0511)),
            projbounds=attributes.get('projbounds',
                                      (-20037508.34, -20037508.34, 20037508.34,
                                       20037508.34))
        )


    @property
    def levels(self):
        """Available levels of the tile system"""
        return self.attributes['levels']

    @property
    def stride(self):
        """Steps along the side of a `Metatile`"""
        return self.attributes['stride']

    @property
    def projcs(self):
        """Projection coodrinate system of the pyramid"""
        return self.attributes['projcs']

    @property
    def geogcs(self):
        """Geographic coordinate system of the pyramid"""
        return self.attributes['geogcs']

    @property
    def geogbounds(self):
        """Boundary of the map in geographic coordinate system"""
        return self.attributes['geogbounds']

    @property
    def projbounds(self):
        """Boundary of the map in projection coordinate system"""
        return self.attributes['projbounds']


class ThemeStorage(ThemeElement):
    """Storage Theme Element

    The `ThemeStorage` contains parameters to setup a
    :class:`~stonemason.provider.tilestorage.ClusterStorage` instance.

    Samples:

    >>> from stonemason.mason.theme.theme import ThemeStorage
    >>> s = ThemeStorage('storage', prototype='disk', parameters=dict(root='.'))
    >>> s.name
    'storage'
    >>> s.prototype
    'disk'
    >>> s.parameters
    {'root': '.'}

    :param name:

        A string literal represents the name of the `ThemeElement`

    :type name: str

    :param prototype:

        A string literal indicates the type of `ClusterStorage` to create.
        There are three available choices, ``null``, ``disk`` and ``s3``. The
        Default value is ``null``.

    :type prototype: str

    :param parameters:

        A dict object contains parameters used to create a `ClusterStorage`
        instance. The default is `{}`.

    :type parameters: dict

    """

    def __init__(self, name, **attributes):
        ThemeElement.__init__(
            self, name,
            prototype=attributes.get('prototype', 'null'),
            tileformat=attributes.get('tileformat',
                                      dict(format='JPEG', extension='jpg')),
            parameters=attributes.get('parameters', dict()))

    @property
    def prototype(self):
        """Prototype of the storage"""
        return self.attributes['prototype']

    @property
    def tileformat(self):
        return self.attributes['tileformat']

    @property
    def parameters(self):
        """Parameters of the storage"""
        return self.attributes['parameters']


class ThemeDesign(ThemeElement):
    def __init__(self, name, **attributes):
        ThemeElement.__init__(
            self, name,
            tileformat=attributes.get('tileformat',
                                      dict(format='JPEG', extension='jpg')),
            layers=attributes.get('layers', dict(root=dict(type='dummy'))))

    @property
    def tileformat(self):
        return self.attributes['tileformat']

    @property
    def layers(self):
        return self.attributes['layers']


class Theme(ThemeRoot):
    """Stonemason Theme

    A `Theme` in stonemason is a configuration object that indicates how and
    where a :class:`~stonemason.provider.tileprovider.TileProvider` retrieve
    its tiles.

    Each `Theme` has a name used to uniquely identify the theme. Also, a theme
    normally has to contain the following elements:

        - :class:`~stonemason.mason.theme.ThemeMetadata`:

            Basic properties of a `Theme`.

        - :class:`~stonemason.mason.theme.ThemePyramid`:

            Properties of the tile system of a `Theme`.

        - :class:`~stonemason.mason.theme.ThemeCache`:

            Properties for setup a
            :class:`~stonemason.provider.tilecache.TileCache` instance.

        - :class:`~stonemason.mason.theme.ThemeStorage`:

            Properties for setup a
            :class:`~stonemason.provider.tilestorage.ClusterStorage` instance.

    Samples:

    >>> from stonemason.mason.theme import Theme
    >>> from stonemason.mason.theme import ThemeMetadata
    >>> t = Theme(name='sample', pyramid=dict(levels=[0, 1, 2]))
    >>> t.name
    'sample'
    >>> t.pyramid.levels
    [0, 1, 2]

    :param name:

        A string literal that uniquely identify a theme. A valid theme name
        should start with an alphabet character and only contain alphanumeric
        character, the underscore and the '@' character. This is equivalent to
        the regular expression :regexp:`^[a-zA-Z][a-zA-Z0-9@_]*$`.

    :type name: str

    :param metadata:

        Basic information about a theme, something like attribution, version.

    :type metadata: :class:`~stonemason.mason.theme.MetadataConfig`

    :param pyramid:

        Properties that defines the tile grid system. It specified properties
        like boundary, zoom levels.

    :type pyramid: :class:`~stonemason.mason.theme.PyramidConfig`

    :param cache:

        Properties that defines the `TileCache` used to cache tiles. It
        could be None to disable the cache.

    :type cache: :class:`~stonemason.mason.theme.CacheConfig`

    :param storage:

        Properties that defines the `ClusterStorage` where tiles are stored.

    :type storage: :class:`~stonemason.mason.theme.StorageConfig`


    """

    def __init__(self, **configs):
        name = configs.get('name', 'default')
        maptype = configs.get('maptype', 'image')

        ThemeRoot.__init__(self, name, maptype=maptype)

        metadata_attrs = configs.get('metadata', dict())
        theme_metadata = ThemeMetadata('metadata', **metadata_attrs)
        self.put_element(theme_metadata.name, theme_metadata)

        pyramid_attrs = configs.get('pyramid', dict())
        theme_pyramid = ThemePyramid('pyramid', **pyramid_attrs)
        self.put_element(theme_pyramid.name, theme_pyramid)

        storage_attrs = configs.get('storage', dict())
        theme_storage = ThemeStorage('storage', **storage_attrs)
        self.put_element(theme_storage.name, theme_storage)

        design_attrs = configs.get('design', dict())
        theme_design = ThemeDesign('design', **design_attrs)
        self.put_element(theme_design.name, theme_design)

    @property
    def metadata(self):
        """Metadata Parameters of the theme"""
        return self.get_element('metadata')

    @property
    def pyramid(self):
        """Pyramid Parameters of the theme"""
        return self.get_element('pyramid')

    @property
    def storage(self):
        """Storage parameters of the theme"""
        return self.get_element('storage')

    @property
    def design(self):
        """Design parameters of the theme"""
        return self.get_element('design')

    def describe(self):
        """Description of the theme"""
        description = dict(
            name=self.name,
            pyramid=self.pyramid.attributes,
            metadata=self.metadata.attributes,
            storage=self.storage.attributes,
            rederer=self.design.attributes
        )

        return description
