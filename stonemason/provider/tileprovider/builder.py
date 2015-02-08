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
    pass


class UnknownPrototype(TileProviderError):
    pass


class TileCacheFactory(object):
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
    def __init__(self, tag, pyramid, metadata=None,
                 cache=None, storage=None):
        self._tag = tag
        self._pyramid = pyramid
        self._metadata = metadata
        self._cache = cache
        self._storage = storage

    def build(self):
        provider = TileProvider(
            tag=self._tag,
            pyramid=self._pyramid,
            metadata=self._metadata,
            cache=self._cache,
            storage=self._storage,
        )

        return provider

    def build_metadata(self, **metadata):
        self._metadata = metadata

    def build_cache(self, **cache_config):
        cache = TileCacheFactory().create(**cache_config)
        self._cache = cache

    def build_storage(self, **storage_config):
        storage = ClusterStorageFactory().create(
            pyramid=self._pyramid, **storage_config)
        self._storage = storage

    def build_design(self, **design):
        self._design = design
