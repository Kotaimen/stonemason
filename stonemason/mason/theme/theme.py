# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the format of stonemason theme.

"""

from stonemason.mason.config import Config

from .block import ModeBlock, MetadataBlock, DesignBlock, CacheBlock, \
    StorageBlock


class Theme(object):
    """ Map Theme

    A ``Theme`` is a specialized config for providers. It contains a bunch of
    config options for creating a provider.

    :type mode: :class:`stonemason.mason.theme.ModeBlock`
    :param mode:

        The mode is a instance of :class:`stonemason.mason.theme.ModeBlock`.
        It is a control element that specifies behaviours of a provider.

    :type metadata: :class:`stonemason.mason.theme.MetadataBlock`
    :param metadata:

        A instance of :class:`stonemason.mason.theme.MetadataBlock` contains
        basic information for a provider to retrieve a tile.

    :type cache: :class:`stonemason.mason.theme.CacheBlock`
    :param cache:

        A instance of :class:`stonemason.mason.theme.CacheBlock` used to
        create a cache storage for a provider cache a tile.

    :type storage: :class:`stonemason.mason.theme.StorageBlock`
    :param storage:

        A instance of :class:`stonemason.mason.theme.StorageBlock` used to
        create a storage where tile stores.

    :type design: :class:`stonemason.mason.theme.DesignBlock`
    :param design:

        A instance of :class:`stonemason.mason.theme.DesignBlock` defines how
        a renderer render a map.

    """

    def __init__(self,
                 mode=None,
                 metadata=None,
                 cache=None,
                 storage=None,
                 design=None):

        if mode is None:
            mode = ModeBlock()
        self._mode = mode

        if metadata is None:
            metadata = MetadataBlock()
        self._metadata = metadata

        if cache is None:
            cache = CacheBlock()
        self._cache = cache

        if storage is None:
            storage = StorageBlock()
        self._storage = storage

        if design is None:
            design = DesignBlock()
        self._design = design

    @staticmethod
    def from_file(filename):
        """Create a theme from a file

        :tyep filename: str
        :param filename:

            Path of a configuration file on your system.
        """
        conf = Config()
        conf.read_from_file(filename)

        mode = conf.get('mode', dict())
        mode_block = ModeBlock(**mode)

        metadata = conf.get('metadata', dict())
        metadata_block = MetadataBlock(**metadata)

        cache = conf.get('cache', dict())
        cache_block = CacheBlock(**cache)

        storage = conf.get('storage', dict())
        storage_block = StorageBlock(**storage)

        design = conf.get('design', dict())
        design_block = DesignBlock(**design)

        return Theme(mode_block, metadata_block, cache_block, storage_block,
                     design_block)

    @property
    def mode(self):
        """`TileProvider` mode"""
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
