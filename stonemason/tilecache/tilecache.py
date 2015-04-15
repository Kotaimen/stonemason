# -*- encoding: utf-8 -*-

"""
    stonemason.tilecache.tilecache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A do nothing tile cache.
"""
__author__ = 'kotaimen'
__date__ = '1/6/15'

from stonemason.pyramid import Tile


class TileCacheError(Exception):
    pass


class TileNotFound(TileCacheError):
    pass


class TileCache(object):  # pragma: no cover
    """A cache for Tiles.

    Cache recent or frequently visited tiles for fast access, also works
    as a intermediate temporary storage for tiles retrieved from `TileStorage`.

    A tile in the cache is identified by its `tag` and `index`.
    `tag` must be a string  matching regular expression
    :regexp:`[a-zA-Z][a-zA-Z0-9_-%]+`, while `index` must be an
    :class:`~stonemason.pyramid.TileIndex` object.

    `TileCache` is designed to be shared between all `themes` and `layers` in
    a particular deployment.
    """

    def get(self, tag, index):
        """Retrieve a tile from cache, return `None` on miss.

        :param tag: Tag of the tile.
        :type tag: str
        :param index: Index of the tile.
        :type index: :class:`~stonemason.pyramid.TileIndex`
        :return: `Tile` object on hit, `None` on miss.
        :rtype: `Tile` or `None`
        """
        raise NotImplementedError

    def has(self, tag, index):
        """Check whether give tag&index exists in the cache.

        Implement may provide a better to check existence instead of actually
        retrieve tile data.

        :param tag: Tag of the tile.
        :type tag: str
        :param index: Index of the tile.
        :type index: :class:`~stonemason.pyramid.TileIndex`
        :return: Whether the tile exists in the cache.
        :rtype: bool
        """
        return self.get(tag, index) is not None

    def put(self, tag, tile, ttl=0):
        """Put a tile into the cache with given tag.

        Put a tile object into the cache, overwriting any existing one, the
        tile will be expired after given `ttl`.

        :param tag: Tag of the tile.
        :type tag: str
        :param tile: Tile to put.
        :type tile: :class:`~stonemason.pyramid.Tile`
        :param ttl: Number of seconds before expiration, `0` means never.
        :type ttl: int
        :return: None
        :raise: :class:`~stonemason.tilecache.TileCacheError` when fail.
        """
        raise NotImplementedError

    def retire(self, tag, index):
        """Delete tile with given tag&index from cache.

        If `tile` does not present in cache, this operation has no effect.

        :param tag: Tag of the tile.
        :type tag: str
        :param index: Index of the tile.
        :type index: :class:`~stonemason.pyramid.TileIndex`
        :return: None
        """
        raise NotImplementedError

    def put_multi(self, tag, tiles, ttl=0):
        """Put many tiles of with same tag in one call.

        Usually this operation is much faster if batching is supported by
        underlying driver. Note usually `put_multi` is *not* atomic.

        :param tag: Tag of the tile.
        :type tag: str
        :param tiles: A iterable of tiles to put.
        :type tiles: list
        :param ttl: Number of seconds before expiration.
        :type ttl: int
        :return: None
        """

        for tile in tiles:
            self.put(tag, tile, ttl=ttl)

    def has_all(self, tag, indexes):
        """Check whether all given tag and tile indexes exist in the cache

        Usually this operation is much faster if batching is supported by
        underlying driver.

        :param tag: Tag of the tile.
        :type tag: str
        :param indexes: A list of tiles to put.
        :type indexes: list
        :return: Whether all given tiles exist in the cache.
        """

        return all(self.has(tag, index) for index in indexes)

    def lock(self, tag, index, ttl=0.1):
        """Mark a particular tile as locked for a specified amount of time.

        Implement pessimistic locking.
        Mark a tile with given tag and index as locked until ttl expires.
        Return a CAS integer which can be used to unlock the tile.
        If the tile is already locked, returns 0.

        :param tag: Tag of the tile.
        :type tag: str
        :param index: Index of the tile.
        :type index: :class:`~stonemason.pyramid.TileIndex`
        :param ttl: Number of seconds before lock expiration.
        :type ttl: int
        :return: CAS on success or zero when tile is already locked.
        """
        assert 1 >= ttl > 0
        return 0xfeed

    def unlock(self, tag, index, cas):
        """Unlock a particular tile using given `cas`.

        The tile must have been locked with the specified `cas`.

        :param tag: Tag of the tile.
        :type tag: str
        :param index: Index of the tile.
        :type index: :class:`~stonemason.pyramid.TileIndex`
        :param cas: CAS value of the tile.
        :type cas: int
        :return: `True` if unlock is successful or no lock is present, `False` otherwise.
        :rtype: bool
        """
        return True

    def flush(self):
        """Delete everything in the cache."""
        raise NotImplementedError

    def close(self):
        """Release any underlying resources.

        .. Warning::
            This will clear everything, include data not stored by TileCache.
        """
        raise NotImplementedError


class NullTileCache(TileCache):
    """A cache that caches nothing."""

    def get(self, tag, index):
        return None

    def has(self, tag, index):
        return False

    def put(self, tag, tile, ttl=0):
        return

    def retire(self, tag, index):
        return

    def put_multi(self, tag, tiles, ttl=0):
        return

    def has_all(self, tag, indexes):
        return False

    def lock(self, tag, index, ttl=0.1):
        return 0xfeed

    def unlock(self, tag, index, cas):
        return True

    def flush(self):
        return

    def close(self):
        return