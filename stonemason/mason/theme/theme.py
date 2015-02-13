# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme and configs for stonemason

"""

__author__ = 'ray'
__date__ = '2/8/15'

import re
from collections import namedtuple


class ThemeError(Exception):
    """Base Theme Exception"""
    pass


# make theme immutable
_Theme = namedtuple('Theme', 'name metadata pyramid cache storage')

_MetadataConfig = namedtuple('MetadataConfig',
                             'version description attribution thumbnail '
                             'center center_zoom')

_PyramidConfig = namedtuple('PyramidConfig', 'levels stride crs proj boundary')

_CacheConfig = namedtuple('CacheConfig', 'prototype parameters')

_StorageConfig = namedtuple('StorageConfig', 'prototype parameters')


class Theme(_Theme):
    """Stonemason Theme

    A configuration that defines how and where a
    :class:`~stonemason.provider.tileprovider.TileProvider` retrieve its tiles.

    Each `Theme` in stonemason has a name, which is also used to identify
    the tiles to retrieve.

    Normally, a theme instance also defines the following configs:

        - :class:`~stonemason.mason.theme.MetadataConfig`:

            Basic information about a `Provider`.

        - :class:`~stonemason.mason.theme.PyramidConfig`:

            Properties that defines the tile Grid of a `Provider`.

        - :class:`~stonemason.mason.theme.CacheConfig`:

            Properties for creating a
            :class:`~stonemason.provider.tilecache.TileCache`.

        - :class:`~stonemason.mason.theme.StorageConfig`:

            Properties for creating a
            :class:`~stonemason.provider.tilestorage.ClusterStorage`.

    Samples:

    >>> from stonemason.mason.theme import Theme
    >>> t = Theme(name='sample')
    >>> t.name
    'sample'
    >>> t.metadata
    MetadataConfig(version='', description='', attribution='K&R', thumbnail=None, center=[0, 0], center_zoom=4)
    >>> t.pyramid
    PyramidConfig(levels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, \
15, 16, 17, 18, 19, 20, 21, 22], stride=1, crs='EPSG:4326', \
proj='EPSG:3857', boundary=(-180, -85.0511, 180, 85.0511))
    >>> t.cache
    CacheConfig(prototype='null', parameters={})
    >>> t.storage
    StorageConfig(prototype='null', parameters={})


    :type name: str
    :param name:

        A string literal that uniquely identify a theme. A valid theme name
        should start with an alphabet character and only contain alphanumeric
        character, the underscore and the '@' character. This is equivalent to
        the regular expression :regexp:`^[a-zA-Z][a-zA-Z0-9@_]*$`.

    :type metadata: :class:`~stonemason.mason.theme.MetadataConfig`
    :param metadata:

        Basic information about a theme, something like attribution, version.

    :type pyramid: :class:`~stonemason.mason.theme.PyramidConfig`
    :param pyramid:

        Properties that defines the tile grid system. It specified properties
        like boundary, zoom levels.

    :type cache: :class:`~stonemason.mason.theme.CacheConfig`
    :param cache:

        Properties that defines the `TileCache` used to cache tiles. It
        could be None to disable the cache.

    :type storage: :class:`~stonemason.mason.theme.StorageConfig`
    :param storage:

        Properties that defines the `ClusterStorage` where tiles are stored.

    """

    __slots__ = ()

    def __new__(cls, name=None, metadata=None,
                pyramid=None, cache=None, storage=None):

        if name is None:
            raise ThemeError('A Theme must have a Name!')

        if not re.match('^[a-zA-Z][a-zA-Z0-9@_]*$', name):
            raise ThemeError(
                """A valid theme name should start with an alphabet character
                and only contain alphanumeric character, the underscore and
                the '@' character.""")

        if metadata is None:
            metadata = MetadataConfig()

        if pyramid is None:
            pyramid = PyramidConfig()

        if cache is None:
            cache = CacheConfig()

        if storage is None:
            storage = StorageConfig()

        assert isinstance(metadata, MetadataConfig)
        assert isinstance(pyramid, PyramidConfig)
        assert isinstance(cache, CacheConfig)
        assert isinstance(storage, StorageConfig)

        return _Theme.__new__(cls, name=name, metadata=metadata,
                              pyramid=pyramid, cache=cache, storage=storage)


class MetadataConfig(_MetadataConfig):
    """Metadata Config

    The `MetadataConfig` is one of the basic building elements of a `Theme`
    that contains basic properties of a theme. Properties in MetadataConfig
    aims to provide better understanding of a Theme.

    Samples:

    >>> from stonemason.mason.theme import MetadataConfig
    >>> m = MetadataConfig(version='0.0.1',
    ...                    description='A sample',
    ...                    attribution='Q',
    ...                    thumbnail='http://localhost/thumb.jpg',
    ...                    center=[139, 35],
    ...                    center_zoom=5)
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

    :type version: str
    :param version:

        A string literal represents the current edition of the `Theme`.

    :type description: str
    :param description:

        A written representation of current `Theme`.

    :type attribution: str
    :param attribution:

        The statement of the copyright author's identity.

    :type thumbnail: str
    :param thumbnail:

        A url that represents the location of thumbnail.

    :type center: list
    :param center:

        A [lon, lat] object that represents the start point of a provider's
        map.

    :type center_zoom: int
    :param center_zoom:

        A positive integer that represents the zoom level of the `center`.

    """

    __slots__ = ()

    def __new__(cls, version='', description='', attribution='K&R',
                thumbnail=None, center=None, center_zoom=4):

        if center is None:
            center = [0, 0]

        return _MetadataConfig.__new__(cls, version=version,
                                       description=description,
                                       attribution=attribution,
                                       thumbnail=thumbnail,
                                       center=center,
                                       center_zoom=center_zoom)


class PyramidConfig(_PyramidConfig):
    """Pyramid Config

    The `PyramidConfig` contains properties used to construct the
    :class:`~stonemason.provider.pyramid.Pyramid` tile grid system.

    Samples:

    >>> from stonemason.mason.theme import PyramidConfig
    >>> p = PyramidConfig(levels=range(0, 5),
    ...                   stride=8,
    ...                   crs='EPSG:4326',
    ...                   proj='EPSG:3857',
    ...                   boundary=(-45, -45, 45, 45))
    >>> p.levels
    [0, 1, 2, 3, 4]
    >>> p.stride
    8
    >>> p.crs
    'EPSG:4326'
    >>> p.proj
    'EPSG:3857'
    >>> p.boundary
    (-45, -45, 45, 45)

    :type levels: list
    :param levels:

        A list of positive integers indicates available levels for the tile
        system. Default values ranges from 0 to 23 (exclusive).

    :type stride: int
    :param stride:

        A positive integer that represents the number of steps along the side
        of a `metatile`. It must be powers of 2. Stride of a 2x2 metatile is
        2. The default value is ``1``.

    :type crs: str
    :param crs:

        A string literal that defines the coordinate reference system(CRS) of
        the available data source. Its validation is delayed to backend. The
        default value is ``EPSG:4326``.

    :type proj: str
    :param proj:

        A string literal that defines the projection of the map. Its
        validation is delayed to backend. The default value is ``EPSG:3857``.

    :type boundary: tuple
    :param boundary:

        Boundary of the map specified in data `crs`. The default value is
        (-180, -85.0511, 180, 85.0511).

    """

    __slots__ = ()

    def __new__(cls, levels=range(0, 23),
                stride=1,
                crs='EPSG:4326',
                proj='EPSG:3857',
                boundary=(-180, -85.0511, 180, 85.0511)):
        return _PyramidConfig.__new__(cls, levels=levels, stride=stride,
                                      crs=crs, proj=proj, boundary=boundary)


class CacheConfig(_CacheConfig):
    """Config for `TileCache`

    The `CacheConfig` contains setup information to create a
    :class:`~stonemason.provider.tilecache.TileCache` in a `TileProvider`.

    The validation of parameters values is delayed to the creation time.

    Samples:

    >>> from stonemason.mason.theme import CacheConfig
    >>> c = CacheConfig(prototype='memcache',
    ...                 parameters=dict(servers=['127.0.0.1']))
    >>> c.prototype
    'memcache'
    >>> c.parameters
    {'servers': ['127.0.0.1']}

    :type prototype: str
    :param prototype:

        A string literal represents the type of `TileCache` to create. For
        now, only ``null`` and ``memcache`` is supported. Default value
        is ``null``.

    :type parameters: dict
    :param parameters:

        A dict object contains options used to create `TileCache`. Default to
        None.

    """

    __slots__ = ()

    def __new__(cls, prototype='null', parameters=None):

        if parameters is None:
            parameters = dict()

        return _CacheConfig.__new__(cls, prototype=prototype,
                                    parameters=parameters)


class StorageConfig(_StorageConfig):
    """Config for `ClusterStorage`

    The `StorageConfig` contains setup information to create a
    :class:`~stonemason.provider.tilestorage.ClusterStorage`
    in a `TileProvider`. The validation of these option values is delayed to
    the creation time.

    Samples:

    >>> from stonemason.mason.theme import StorageConfig
    >>> s = StorageConfig(prototype='disk',
    ...                   parameters=dict(root='/tmp/themes/'))
    >>> s.prototype
    'disk'
    >>> s.parameters
    {'root': '/tmp/themes/'}

    :type prototype: str
    :param prototype:

        A string literal represents the type of `ClusterStorage` to create.
        Three choice, ``null``, ``disk`` and ``s3``, are available. Default
        value is ``null``.

    :type parameters: dict
    :param parameters:

        A dict object contains options used to create `ClusterStorage`.
        The default is None.

    """

    __slots__ = ()

    def __new__(cls, prototype='null', parameters=None):

        if parameters is None:
            parameters = dict()

        return _StorageConfig.__new__(cls, prototype=prototype,
                                      parameters=parameters)

