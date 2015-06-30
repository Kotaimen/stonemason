# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements Theme Configuration for stonemason.

"""

__author__ = 'ray'
__date__ = '3/30/15'


class DictTheme(object):
    """Dict Theme

    `DictTheme` is the general configuration object for setting parameters. It
    could takes a dictionary as configuration and get attribute with the given
    name.

    """

    def __init__(self, **config):
        self._config = config

    def get_attribute(self, key, default=None):
        """Get attribute with the key"""
        return self._config.get(key, default)

    def to_dict(self):
        """Return a dict of all the attributes"""
        return self._config

    def __repr__(self):
        return repr(self._config)


class SchemaTheme(DictTheme):
    """Schema Theme

    A `SchemaTheme` object configs attributes for a
    :class:`~stonemason.mason.mapsheet.MapSheet`.

    """

    @property
    def tag(self):
        """Return a Tag identifier"""
        return self.get_attribute('tag')

    @property
    def maptype(self):
        """Return a string literal indicates the map type"""
        return self.get_attribute('maptype')

    @property
    def tileformat(self):
        """Return a dict of tile format configs"""
        return self.get_attribute('tileformat')

    @property
    def pyramid(self):
        """Coordinate reference system of the `MapSheet`"""
        return self.get_attribute('pyramid')

    @property
    def storage(self):
        """A dict of configs for tile cache storage"""
        return self.get_attribute('storage')

    @property
    def renderer(self):
        """A dict of configs for map renderer"""
        return self.get_attribute('renderer')


class Theme(DictTheme):
    """Theme

    A `Theme` object configs a :class:`~stonemason.mason.mapbook.MapBook`
    in stonemason. It takes a dict as an input which stores
    attributes to setup a `MapBook` according the theme specification.

    In the dict config, you could specify all attributes that is needed
    to setup a `MapBook`, such as name, metadata and map sheets.

    Each `MapBook` contains a bunch of map sheets, just like a book is
    consists of a pile of pages. And configs for these sheets are defined in
    the `schemas` of the theme as a list of dict.

    The dict config specification is defined as followings:

        `name`

            A string literal that uniquely identifies the `MapBook`.

        `metadata`

            Additional information about the `MapBook`.

        `schemas`

            List of configs for setup a
            :class:`~stonemason.mason.mapsheet.MapSheet`.

            Configs of one Map Sheet are available as the followings:

                `tag`

                    A string literal that uniquely identifies the `MapSheet`.

                `pyramid`

                    The coordinate reference system of the map.

                `maptype`

                    The type of the map. Available options are ``image``,
                    ``vector`` and ``raster``.

                `tileformat`

                    The format of output tiles. for example, {'format': 'PNG'}.

                `storage`

                    (Optional) configs for cached tile storage.

                `renderer`

                    (Optional) configs for ad-hoc renderer.

    Here is a simple theme example with one schema:

    >>> from stonemason.mason.theme import Theme
    >>> config = dict(
    ...         name='sample',
    ...         metadata={'version': '1.0.0'},
    ...         schemas=[{
    ...             'tag': '.png',
    ...             'pyramid': {'stride': 2},
    ...             'maptype': 'image',
    ...             'tileformat': {'format': 'PNG'},
    ...             'storage': {
    ...                     'prototype': 'disk',
    ...                     'stride': 8,
    ...                     'root': './cache'
    ...                 }
    ...             }]
    ...         )
    >>> t = Theme(**config)
    >>> t.name
    'sample'
    >>> t.metadata
    {'version': '1.0.0'}
    >>> schema = list(s for s in t.schemas)[0]
    >>> schema.tag
    '.png'
    >>> schema.pyramid
    {'stride': 2}
    >>> schema.maptype
    'image'
    >>> schema.tileformat
    {'format': 'PNG'}
    >>> schema.storage['prototype']
    'disk'

    """

    @property
    def name(self):
        """Name for the MapBook"""
        return self.get_attribute('name')

    @property
    def metadata(self):
        """Metadata of the MapBook """
        return self.get_attribute('metadata')

    @property
    def schemas(self):
        """A iterator of configs for Map Sheets"""
        for schema in self.get_attribute('schemas', default=list()):
            yield SchemaTheme(**schema)
