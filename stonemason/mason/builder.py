# -*- encoding: utf-8 -*-
"""
    stonemason.mason.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements TileProvider Factory

"""

__author__ = 'ray'
__date__ = '2/5/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.provider.tilecache import NullTileCache, MemTileCache
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage
from stonemason.provider.tileprovider.provider import TileProvider

from .theme import Theme


class BuilderError(Exception):
    """Base Tile Provider Error"""
    pass


class UnknownCachePrototype(BuilderError):
    """Unknown cache prototype"""
    pass


class UnknownStoragePrototype(BuilderError):
    """Unknown storage prototype"""
    pass


class TileCacheFactory(object):
    """`TileCache` Factory
    """

    KNOWN_CACHES = {
        'memcache': MemTileCache
    }

    def create(self, prototype, **parameters):
        """Create a `TileCache` instance

        :param prototype: Prototype of the cache.
        :type prototype: str

        :param kwargs: Parameters for the specified `TileCache`.
        :type kwargs: dict

        """
        if prototype == 'null':
            return NullTileCache()

        constructor = self.KNOWN_CACHES.get(prototype)
        if constructor is None:
            raise UnknownCachePrototype(prototype)

        return constructor(**parameters)


class ClusterStorageFactory(object):
    """`ClusterStorage` Factory
    """

    KNOWN_CLUSTER_STORAGE = {
        'disk': DiskClusterStorage,
        's3': S3ClusterStorage
    }


    def create(self, prototype, pyramid, formatbundle, **parameters):
        """Create a `ClusterStorage` instance

        :param pyramid: An instance of `Pyramid`.
        :type pyramid: :class:`~stonemason.pyramid.Pyramid`

        :param kwargs: A dict contains parameters for creating a `ClusterStorage`.
        :type kwargs: dict

        """

        if prototype == 'null':
            return NullClusterStorage()

        constructor = self.KNOWN_CLUSTER_STORAGE.get(prototype)
        if constructor is None:
            raise UnknownStoragePrototype(prototype)

        return constructor(pyramid=pyramid, format=formatbundle, **parameters)


class TileProviderFactory(object):
    """`TileProvider` Builder

    `TileProviderFactory` builds `TileProvider` from themes.

    An additional cache config could be taken to override the cache settings
    in the theme, which is often used in seperate .
    """

    def __init__(self):
        self._cache_factory = TileCacheFactory()
        self._storage_factory = ClusterStorageFactory()

    def create_from_theme(self, tag, theme, external_cache=None):
        """Build `TileProvider` from a stonemason theme

        :param theme: A stonemason `Theme` instance.
        :type theme: :class:`~stonemason.mason.theme.Theme`

        :param cache_config: A dict contains configs for creating a `TileCache`.
        :type cache_config: dict
        """
        assert isinstance(theme, Theme)
        assert isinstance(external_cache, dict) or external_cache is None

        tag = tag

        pyramid = self._build_pyramid_from_theme(theme)

        metadata = self._build_metadata_from_theme(theme)

        cache = self._build_cache_from_theme(theme, external_cache)

        storage = self._build_storage_from_theme(theme)

        provider = TileProvider(
            tag, pyramid, metadata=metadata, cache=cache, storage=storage)

        return provider

    def _build_metadata_from_theme(self, theme):
        return dict(theme.metadata.attributes)

    def _build_pyramid_from_theme(self, theme):
        return Pyramid(**theme.pyramid.attributes)

    def _build_cache_from_theme(self, theme, external_cache=None):

        if external_cache is None:
            prototype = theme.cache.prototype
            parameters = theme.cache.parameters

        else:
            assert isinstance(external_cache, dict)

            prototype = external_cache.get('prototype', 'null')
            parameters = external_cache.get('parameters', dict())

        cache = self._cache_factory.create(prototype, **parameters)

        return cache

    def _build_storage_from_theme(self, theme):

        prototype = theme.storage.prototype

        pyramid = Pyramid(**theme.pyramid.attributes)

        maptype = MapType(theme.maptype)
        tileformat = TileFormat(**theme.storage.tileformat)
        bundle = FormatBundle(maptype, tileformat)

        parameters = theme.storage.parameters

        storage = self._storage_factory.create(
            prototype, pyramid, bundle, **parameters)

        return storage
