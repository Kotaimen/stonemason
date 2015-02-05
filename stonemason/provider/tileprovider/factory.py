# -*- encoding: utf-8 -*-
"""
    stonemason.provider.tileprovider.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements TileProvider Factory

"""

__author__ = 'ray'
__date__ = '1/31/15'

from stonemason.provider.tilecache import NullTileCache, MemTileCache
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage

from .provider import TileProvider


class TileProviderError(Exception):
    pass


class UnknownCacheType(TileProviderError):
    pass


class UnknownStorageType(TileProviderError):
    pass


class TileCacheFactory(object):
    """``TileCache`` Factory

    A factory class that creates an instance of ``TileCache``.

    :type prototype: str
    :param prototype:

        A string literal represents the kind of ``TileCache`` to create.

        - null:

            Create a :class:`stonemason.provider.tilecache.NullTileCache`.

        - memcache:

            Create a :class:`stonemason.provider.tilecache.MemTileCache`.

    :type kwargs: dict
    :param kwargs:

        Parameters for creating a ``TileCache`` instance.

    """

    def create(self, **kwargs):
        """Create a ``TileCache`` instance"""

        prototype = kwargs.get('prototype')

        if prototype == 'null':
            return NullTileCache()
        elif prototype == 'memcache':
            return MemTileCache(**kwargs)
        else:
            raise UnknownCacheType(prototype)


class ClusterStorageFactory(object):
    """``ClusterStorage`` Factory

    A factory class that creates an instance of ``ClusterStorage``.

    :type prototype: str
    :param prototype:

        A string literal represents the kind of ``ClusterStorage`` to create.

        - null:

            Create a :class:`stonemason.provider.tilestorage.NullClusterStorage`.

        - disk:

            Create a :class:`stonemason.provider.tilecache.DiskClusterStorage`.

        - s3:

            Create a :class:`stonemason.provider.tilecache.S3ClusterStorage`.

    :type kwargs: dict
    :param kwargs:

        Parameters for creating a ``TileCache`` instance.

    """

    def create(self, **kwargs):
        """Create a ``ClusterStorage`` instance."""

        prototype = kwargs.get('prototype')

        if prototype == 'null':
            return NullClusterStorage()
        elif prototype == 'disk':
            return DiskClusterStorage(**kwargs)
        elif prototype == 's3':
            return S3ClusterStorage(**kwargs)
        else:
            raise UnknownStorageType(prototype)


class TileProviderBuilder(object):
    """TileProvider Factory

    Build a tile provider with given configs.
    """

    MODE_READ_ONLY = 'read-only'

    def build(self, tag, mode='read-only', metadata=None, cache_conf=None,
              storage_conf=None, design_conf=None):
        """Build a tile provider

        :type tag: str
        :param tag:

            A string literal uniquely identifies a provider.

        :type mode: str
        :param mode:

            A string literal controls behaviours of a provider. In ``read-only``
            mode, a provider will ignore caches and retrieve tile directly from
            the storage. And in ``hybrid`` mode, tile will be retrieved from the
            cache before hitting a persistent storage.

        :type metadata: dict
        :param metadata:

            A dict object contains basic information of a provider.

        :type cache_conf: dict
        :param cache_conf:

            A dict object contains configuration of a ``TileCache``.

        :type storage_conf: dict
        :param storage_conf:

            A dict object contains configuration of a ``TileStorage``.

        :rtype: :class:`~stonemason.provider.tileprovider.TileProvider`
        :return: Return a provider.

        Samples:

        Create a dummy provider always returns none.

        >>> from stonemason.provider.tileprovider import TileProviderBuilder
        >>> provider = TileProviderBuilder().build(tag='test')
        >>> provider.tag
        'test'
        >>> provider.metadata
        {}
        >>> tile = provider.get_tile(0, 0, 0)
        >>> tile is None
        True

        """

        if mode == self.MODE_READ_ONLY or cache_conf is None:
            cache = NullTileCache()
        else:
            cache_conf = cache_conf
            cache = TileCacheFactory().create(**cache_conf)

        if storage_conf is None:
            storage = NullClusterStorage()
        else:
            storage = ClusterStorageFactory().create(**storage_conf)

        return TileProvider(tag, metadata, cache=cache, storage=storage)


