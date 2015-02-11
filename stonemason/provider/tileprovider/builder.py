# -*- encoding: utf-8 -*-
"""
    stonemason.provider.tileprovider.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements TileProvider Factory

"""

__author__ = 'ray'
__date__ = '2/5/15'

from stonemason.provider.tilecache import NullTileCache, MemTileCache
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage

from .provider import TileProvider


class TileProviderError(Exception):
    """Base Tile Provider Error"""
    pass


class UnknownPrototype(TileProviderError):
    """Unknown cache or storage prototype"""
    pass


class TileCacheFactory(object):
    """`TileCache` Factory"""

    def create(self, **kwargs):
        prototype = kwargs.get('prototype')
        parameters = kwargs.get('parameters')

        if prototype == 'null':
            return NullTileCache()
        elif prototype == 'memcache':
            return MemTileCache(**parameters)
        else:
            raise UnknownPrototype(prototype)


class ClusterStorageFactory(object):
    """`ClusterStorage` Factory"""

    def create(self, pyramid, **kwargs):
        prototype = kwargs.get('prototype')
        parameters = kwargs.get('parameters')

        if prototype == 'null':
            return NullClusterStorage()
        elif prototype == 'disk':
            return DiskClusterStorage(pyramid=pyramid, **parameters)
        elif prototype == 's3':
            return S3ClusterStorage(pyramid=pyramid, **parameters)
        else:
            raise UnknownPrototype(prototype)


class TileProviderBuilder(object):
    """`TileProvider` Builder

    A `TileProviderBuilder` builds `TileProvider` from a bunch of configs.

    Name and `Pyramid` is required for a basic TileProvider.

    It is advised to add `TileCache` or `ClusterStorage` for building a fully
    functional `TileProvider`.

    :type tag: str
    :param tag:

        Name of the provider.

    :type pyramid: :class:`stonemason.provider.pyramid.Pyramid`
    :param pyramid:

        The tile system of the provider.

    :type metadata: dict
    :param metadata:

        Metadata infromation of the provider.

    :type cache: :class:`stonemason.provider.tilecache.TileCache`
    :param cache:

        A TileCache instance used to cache tiles.

    :type storage: :class:`stonemason.provider.tilestorage.ClusterStorage`
    :param storage:

        A ClusterStorage instance used to store or retrieve tiles.

    """
    def __init__(self, tag, pyramid, metadata=None, cache=None, storage=None):
        self._tag = tag
        self._pyramid = pyramid
        self._metadata = metadata
        self._cache = cache
        self._storage = storage

    def build(self):
        """Build a `TileProvider`

        :rtype: :class:`stonemason.provider.tileprovider.TileProvider`
        :return: Return a `TileProvider` with previous build.

        """
        provider = TileProvider(
            tag=self._tag,
            pyramid=self._pyramid,
            metadata=self._metadata,
            cache=self._cache,
            storage=self._storage,
        )

        return provider

    def build_metadata(self, **metadata):
        """Create metadata from configs for `TileProvider`
        """
        self._metadata = metadata

    def build_cache(self, **cache_config):
        """Create `TileStorage` from configs for `TileProvider`
        """
        cache = TileCacheFactory().create(**cache_config)
        self._cache = cache

    def build_storage(self, **storage_config):
        """Create `ClusterStorage` from configs for `TileProvider`
        """
        storage = ClusterStorageFactory().create(
            pyramid=self._pyramid, **storage_config)
        self._storage = storage

    def build_design(self, **design):
        self._design = design
