# -*- encoding: utf-8 -*-
"""
    stonemason.provider.tileprovider.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements Tile Provider.

"""

import six

from stonemason.provider.pyramid import Pyramid, TileIndex, MetaTileIndex
from stonemason.provider.tilecache import TileCache, NullTileCache
from stonemason.provider.tilestorage import ClusterStorage, NullClusterStorage


class ProviderError(object):
    """Base TileProvider Error"""
    pass


class TileProvider(object):
    """Tile Provider

    A ``TileProvider`` retrieve tiles from a cache or storage with a given
    grid coordinate (z, x, y).

    :type tag: str
    :param tag:

        A string literal that identifies a ``TileProvider``.

    :type metadata: dict
    :param metadata:

        A dict object contains information about a provider.

    :type cache: :class:`~stonemason.provider.tilecache.TileCache`
    :param cache:

        A ``TileCache`` instance used to cache retrieved tile.

    :type storage: :class:`~stonemason.provider.tilestorage.ClusterStorage`
    :param storage:

        A ``TileStorage`` instance where tiles are stored.

    """

    TILEPROVIDER_MODE_READONLY = 'read-only'

    TILEPROVIDER_MODE_HYBRID = 'hybrid'

    def __init__(self, tag, pyramid, metadata=None,
                 cache=None, storage=None, mode='read-only'):
        assert isinstance(tag, six.string_types)
        assert isinstance(pyramid, Pyramid)
        assert isinstance(metadata, dict) or metadata is None
        assert isinstance(cache, TileCache) or cache is None
        assert isinstance(storage, ClusterStorage) or storage is None

        self._tag = tag
        self._pyramid = pyramid
        self._mode = mode

        if metadata is None:
            metadata = dict()
        self._metadata = metadata

        if cache is None:
            cache = NullTileCache()
        self._cache = cache

        if storage is None:
            storage = NullClusterStorage()
        self._storage = storage

    @property
    def tag(self):
        """Name of the provider"""
        return self._tag

    @property
    def pyramid(self):
        """Pyramid of the """
        return self._pyramid

    @property
    def metadata(self):
        """Metadata of the provider"""
        return self._metadata

    @property
    def mode(self):
        """Get working mode of the provider"""
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Set working mode of the provider"""
        self._mode = mode

    def get_tile(self, z, x, y):
        """Return a tile with given coordinate

        :type z: int
        :param z:

            Zoom level.

        :type x: int
        :param x:

            Horizontal axis.

        :type y: int
        :param y:

            Vertical axis.

        :rtype: :class:`~stonemason.provider.pyramid.Tile` or None
        :return: A ``Tile`` object or None if not found.

        """
        index = TileIndex(z, x, y)

        # get from cache
        if self.mode != self.TILEPROVIDER_MODE_READONLY:
            tile = self._cache.get(self.tag, index)
            if tile is not None:
                return tile

        # get from storage
        meta_index = MetaTileIndex(z, x, y, self._pyramid.stride)

        cluster = self._storage.get(meta_index)
        if cluster is not None:
            for t in cluster.tiles:
                if t.index == index:
                    tile = t
                    break
            else:
                assert False
        else:
            tile = None

            # refill the cache if tile is not None
        if self.mode != self.TILEPROVIDER_MODE_READONLY and tile is not None:
            self._cache.put_multi(self.tag, cluster.tiles)

        return tile

    def describe(self):
        """Description of a ``TileProvider``"""
        return dict(
            tag=self.tag,
            pyramid=dict(self.pyramid._asdict()),
            metadata=self.metadata
        )

    def close(self):
        """Close resources"""
        self._cache.close()
        self._storage.close()

