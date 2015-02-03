# -*- encoding: utf-8 -*-
"""
    stonemason.provider.tileprovider.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements Tile Provider.

"""

from stonemason.provider.pyramid import TileIndex
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

    :type cache: :class:`stonemason.provider.tilecache.TileCache`
    :param cache:

        A ``TileCache`` instance used to cache retrieved tile.

    :type storage: :class:`stonemason.provider.tilestorage.TileStorage`
    :param storage:

        A ``TileStorage`` instance where tiles are stored.

    """


    def __init__(self, tag, metadata=None, cache=None, storage=None):
        assert isinstance(metadata, dict) or metadata is None
        assert isinstance(cache, TileCache) or cache is None
        assert isinstance(storage, ClusterStorage) or storage is None

        self._tag = tag

        if cache is None:
            cache = NullTileCache()
        self._cache = cache

        if storage is None:
            storage = NullClusterStorage()
        self._storage = storage

        if metadata is None:
            metadata = dict()
        self._metadata = metadata

    @property
    def tag(self):
        """Name of the provider"""
        return self._tag

    @property
    def metadata(self):
        """Metadata of the provider"""
        return self._metadata

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

        :return: A ``Tile`` object or None if not found.
        :rtype: :class:`stonemason.provider.pyramid.Tile` or None
        """
        index = TileIndex(z, x, y)

        # get from cache
        tile = self._cache.get(self.tag, index)
        if tile is None:

            # get from storage
            tile = self._storage.get(index)
            if tile is not None:
                # fill the cache if tile is not None
                self._cache.put(self.tag, index)

        return tile

    def close(self):
        """Close resources"""
        pass

