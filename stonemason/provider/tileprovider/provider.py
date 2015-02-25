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


class TileProvider(object):
    """Tile Provider

    A `TileProvider` retrieve tiles from a cache or storage with a given
    grid coordinate (z, x, y).

    :type tag: str
    :param tag:

        A string literal that identifies a `TileProvider`.

    :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`
    :param metadata:

        The tile grid system of the `TileProvider`.

    :type metadata: dict
    :param metadata:

        Additional information of the `TileProvider`.

    :type cache: :class:`~stonemason.provider.tilecache.TileCache`
    :param cache:

        A `TileCache` instance used to cache tiles.

    :type storage: :class:`~stonemason.provider.tilestorage.ClusterStorage`
    :param storage:

        A `TileStorage` instance used to retrieve tiles.

    :type mode: str
    :param mode:

        A string literal that represents the working behaviours of the
        `TileProvider`. Available options are ``read-only`` and ``hybrid``

    """

    def __init__(self, tag, pyramid, metadata=None,
                 cache=None, storage=None, readonly=False):

        # setting up default values
        if metadata is None:
            metadata = dict()
        if cache is None:
            cache = NullTileCache()
        if storage is None:
            storage = NullClusterStorage()

        assert isinstance(pyramid, Pyramid)
        assert isinstance(metadata, dict)
        assert isinstance(cache, TileCache)
        assert isinstance(storage, ClusterStorage)

        self._tag = tag
        self._pyramid = pyramid
        self._metadata = metadata
        self._cache = cache
        self._storage = storage

        self._readonly = readonly

    @property
    def tag(self):
        """Return name of the provider

        :rtype: str
        :return: Name of the `TileProvider`

        """
        return self._tag

    @property
    def pyramid(self):
        """Return pyramid of the provider

        :rtype: :class:`~stonemason.provider.pyramid.Pyramid`
        :return: Pyramid of the `TileProvider`

        """
        return self._pyramid

    @property
    def metadata(self):
        """Return metadata of the provider

        :rtype: dict
        :return: A dict of basic information about the `TileProvider`

        """
        return self._metadata

    @property
    def readonly(self):
        """Return working mode of the provider

        :rtype: str
        :return: Working behaviour of the `TileProvider`

        """
        return self._readonly

    @readonly.setter
    def readonly(self, val):
        """Set working mode of the provider

        :type mode: str
        :param mode: Working behaviour of the `TileProvider`

        """
        self._readonly = val

    def get_tile(self, z, x, y):
        """Return a tile with given coordinate

        :type z: int
        :param z:

            A positive integer represents the zoom level of a tile.

        :type x: int
        :param x:

            A positive integer represents coordinate along x-axis.

        :type y: int
        :param y:

            A positive integer represents coordinate along y-axis.

        :rtype: :class:`~stonemason.provider.pyramid.Tile` or None
        :return: A `Tile` object or None if not found.

        """
        index = TileIndex(z, x, y)

        # get from cache
        if not self.readonly:
            tile = self._cache.get(self.tag, index)
            if tile is not None:  # cache hit
                return tile

        # get from storage
        meta_index = MetaTileIndex.from_tile_index(index, self._pyramid.stride)

        cluster = self._storage.get(meta_index)
        if cluster is None:  # cluster miss
            return None

        # cluster hit
        tile = cluster[index]

        # refill the cache if tile is not None
        if not self.readonly:
            self._cache.put_multi(self.tag, cluster.tiles)

        return tile

    def close(self):
        """Close resources"""
        self._cache.close()
        self._storage.close()


