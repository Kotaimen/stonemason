# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the format of stonemason theme.

"""

from .themeblock import MetadataBlock, DesignBlock, CacheBlock, StorageBlock


class ThemeError(Exception):
    """Base Theme Error"""
    pass


class ModeNotSupported(ThemeError):
    """Unsupported theme mode"""
    pass


class Theme(object):
    """ Map Theme

    The theme object is a specialized config for providers.
    It defines cache, storage, design and a bunch of options of
    a map provider.

    `config`

        :class:`stonemason.mason.config.Config`

    """

    def __init__(self, config):
        self._name = config.get('name')

        conf = config.get('metadata', dict())
        if not isinstance(self._metadata, dict):
            raise ThemeError('A metadata should be a dict of options!')
        self._metadata = MetadataBlock(**conf)

        self._mode = None
        self._design = None
        self._cache = None
        self._storage = None


    @property
    def name(self):
        """Name of the theme"""
        return self._name

    @property
    def mode(self):
        """Provider mode"""
        return self._mode

    @property
    def metadata(self):
        """Metadata of the theme"""
        return self._metadata

    @property
    def cache(self):
        """Cache configuration"""
        return self._cache

    @property
    def storage(self):
        """Storage configuration"""
        return self._storage

    @property
    def design(self):
        """Map design for renderer"""
        return self._design
