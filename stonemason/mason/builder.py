# -*- encoding: utf-8 -*-
"""
    stonemason.mason.builder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements TileProvider Factory

"""

__author__ = 'ray'
__date__ = '2/5/15'

from stonemason.provider.pyramid import Pyramid
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

    def create(self, **kwargs):
        """Create a `TileCache` instance

        :param kwargs: A dict contains parameters for creating a `TileCache`.
        :type kwargs: dict

        """
        prototype = kwargs.get('prototype')
        parameters = kwargs.get('parameters')

        if prototype == 'null':
            return NullTileCache()

        elif prototype == 'memcache':
            return MemTileCache(**parameters)

        else:
            raise UnknownCachePrototype(prototype)


class ClusterStorageFactory(object):
    """`ClusterStorage` Factory
    """

    def create(self, pyramid, **kwargs):
        """Create a `ClusterStorage` instance

        :param pyramid: An instance of `Pyramid`.
        :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`

        :param kwargs: A dict contains parameters for creating a `ClusterStorage`.
        :type kwargs: dict

        """
        prototype = kwargs.get('prototype')
        parameters = kwargs.get('parameters')

        # XXX: Use hard-wired format bundle for integration
        format_bundle = FormatBundle(MapType('image'),
                                     TileFormat('JPEG'))



        if prototype == 'null':
            return NullClusterStorage()

        elif prototype == 'disk':
            return DiskClusterStorage(pyramid=pyramid,
                                      format=format_bundle,
                                      **parameters)

        elif prototype == 's3':
            return S3ClusterStorage(pyramid=pyramid,
                                    format=format_bundle,
                                    **parameters)

        else:
            raise UnknownStoragePrototype(prototype)


class TileProviderFactory(object):
    """`TileProvider` Builder

    `TileProviderFactory` builds `TileProvider` from themes.

    An additional cache config could be taken to override the cache settings
    in the theme, which is often used in seperate .
    """

    def __init__(self):
        self._cache_factory = TileCacheFactory()
        self._storage_factory = ClusterStorageFactory()

    def create_from_theme(self, tag, theme, cache_config=None):
        """Build `TileProvider` from a stonemason theme

        :param theme: A stonemason `Theme` instance.
        :type theme: :class:`~stonemason.mason.theme.Theme`

        :param cache_config: A dict contains configs for creating a `TileCache`.
        :type cache_config: dict
        """
        assert isinstance(theme, Theme)
        assert isinstance(cache_config, dict) or cache_config is None

        tag = tag
        pyramid = Pyramid(**theme.pyramid.attributes)
        metadata = theme.metadata.attributes

        if cache_config is None:
            cache = self._cache_factory.create(**theme.cache.attributes)
        else:
            assert isinstance(cache_config, dict)
            cache = self._cache_factory.create(**cache_config)

        storage = self._storage_factory.create(
            pyramid, **theme.storage.attributes)

        provider = TileProvider(
            tag, pyramid, metadata=metadata, cache=cache, storage=storage)

        return provider
