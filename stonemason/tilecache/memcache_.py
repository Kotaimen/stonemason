# -*- encoding: utf-8 -*-

"""
    stonemason.tilecache.memcache_
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Memcached tile cache
"""
__author__ = 'kotaimen'
__date__ = '1/12/15'

import re
import json
import random

import pylibmc

from stonemason.pyramid import Tile, TileIndex
from .tilecache import TileCache, TileCacheError


class MemTileCacheError(TileCacheError):
    pass


class MemTileCache(TileCache):
    """A tile cache based on `memcached` protocol backend.

    Tile cache based on `pylibmc`_ protocol backend. The backend does not
    necessary being `memcached` itself, any storage or proxy talks its
    protocol will work, like `couchbase`_ or `nutcracker`_.

    .. Note::

        ``memcached`` has a limit on cache object size, usually its ``4MB``.

    .. _memcached: <http://memcached.org/>
    .. _pylibmc: <http://sendapatch.se/projects/pylibmc/>
    .. _couchbase: <http://www.couchbase.com/>
    .. _nutcracker:  <https://github.com/twitter/twemproxy>

    >>> from stonemason.pyramid import Tile,TileIndex
    >>> from stonemason.tilecache import MemTileCache
    >>> cache = MemTileCache(servers=['localhost:11211',])
    >>> cache.put('layer', Tile(TileIndex(3, 4, 5), b'tile'))
    >>> cache.has('layer', TileIndex(3, 4, 5))
    True
    >>> cache.get('layer', TileIndex(3, 4, 5))
    Tile(3/4/5)
    >>> cache.retire('layer', TileIndex(3, 4, 5))
    >>> cache.has('layer', TileIndex(3, 4, 5))
    False

    :param servers: A list of memcache cluster servers, default value is
        ``['localhost:11211',]``.
    :type servers: list

    :param behaviors: `pylibmc` behaviors,
        .. seealso:: `pylibmc` `behaviours <http://sendapatch.se/projects/pylibmc/behaviors.html>`_.
    :type behaviors: dict or `None`
    """

    def __init__(self, servers=['localhost:11211'],
                 binary=True,
                 behaviors=None):
        super(TileCache, self).__init__()
        if behaviors is None:
            behaviors = {
                # 'tcp_nodelay': True,
                'ketama': True,
                # 'remove_failed': False,
                'cas': True,
                # 'retry_timeout': 1,
                # 'dead_timeout': 60,
            }
        self.connection = pylibmc.Client(servers, binary=binary,
                                         behaviors=behaviors)
        # Verify connection
        try:
            self.connection.get_stats()
        except pylibmc.Error as e:
            raise MemTileCacheError("Can't connect to memcache servers.")

    def _make_key(self, tag, index):
        """Generate `memcached` keys from given `tag` and `index`.

        A tile is stored in three objects in `memcached`:

        ``{tag}/{z}/{x}/{y}``

            tile data as binary data.

        ``{tag}/{z}/{x}/{y}~metadata``

            ``(mimetype, mtime, etag)`` tuple as `json`.

        ``{tag}/{z}/{x}/{y}~lock``

            Optional lock.
        """
        # tag/z/x/y
        # tag/z/x/y~metadata
        # tag/z/x/y~lock
        assert re.match(r'[a-zA-Z][a-zA-Z0-9_\-%]+', tag)
        assert isinstance(index, TileIndex)
        coord = '/'.join(map(str, index))

        key = '%s/%s' % (tag, coord)
        metadata_key = key + '~metadata'
        lock_key = key + '~lock'

        return key, metadata_key, lock_key

    def _make_metadata(self, tile):
        return json.dumps((tile.mimetype, tile.mtime, tile.etag))

    def _load_metadata(self, data):
        return tuple(json.loads(data))

    def get(self, tag, index):
        key, metadata_key, _ = self._make_key(tag, index)

        # get data and metadata in a single call
        try:
            values = self.connection.get_multi([key, metadata_key])
        except pylibmc.Error as e:
            raise MemTileCacheError('Pylibmc error: %r' % e)

        try:
            data = values[key]
            metadata = values[metadata_key]
        except KeyError:
            # only successful when both keys are retrieved
            return None

        try:
            mimetype, mtime, etag = self._load_metadata(metadata)
        except ValueError:
            raise MemTileCacheError('Invalid metadata: "%s"' % metadata_key)

        return Tile(index, data, mimetype, mtime, etag)

    def put(self, tag, tile, ttl=0):
        key, metadata_key, _ = self._make_key(tag, tile.index)
        metadata = self._make_metadata(tile)
        data = {
            key: tile.data,
            metadata_key: metadata
        }
        try:
            failed = self.connection.set_multi(data, time=ttl)
        except pylibmc.Error as e:
            raise MemTileCacheError('Pylibmc error: %r' % e)

        if len(failed) > 0:
            raise MemTileCacheError('Tile not writen: "%s"' % failed)

    def has(self, tag, index):
        _, metadata_key, _ = self._make_key(tag, index)
        try:
            return self.connection.get(metadata_key) is not None
        except pylibmc.Error as e:
            return None

    def retire(self, tag, index):
        key, metadata_key, _ = self._make_key(tag, index)
        try:
            self.connection.delete_multi([key, metadata_key])
        except pylibmc.Error as e:
            pass

    def put_multi(self, tag, tiles, ttl=0):
        assert tiles
        data = {}
        n = 0
        for n, tile in enumerate(tiles):
            key, metadata_key, _ = self._make_key(tag, tile.index)
            data[key] = tile.data
            data[metadata_key] = self._make_metadata(tile)
        else:
            assert len(data) == (n + 1) * 2

        try:
            failed = self.connection.set_multi(data, time=ttl)
        except pylibmc.Error as e:
            raise MemTileCacheError('Pylibmc error: %r' % e)

        if len(failed) > 0:
            raise MemTileCacheError('Tile not writen: "%s"' % len(failed))

    def lock(self, tag, index, ttl=0.1):
        # memcache only supports integer ttl...
        ttl = int(round(ttl, 0))
        # never allow ttl=0 since it means lock forever
        if ttl <= 0:
            ttl = 1

        _, _, lock_key = self._make_key(tag, index)

        # check lock
        try:
            ret = self.connection.get(lock_key)
        except pylibmc.Error as e:
            return 0

        if ret is not None:
            # already locked
            return 0
        else:
            # XXX: potential random collision
            cas = random.getrandbits(31)
            try:
                self.connection.set(lock_key, cas, time=ttl)
            except pylibmc.Error as e:
                return 0
            else:
                return cas

    def unlock(self, tag, index, cas):
        _, _, lock_key = self._make_key(tag, index)

        try:
            value = self.connection.get(lock_key)
        except pylibmc.Error as e:
            return True

        if value is None:
            # already unlocked
            return True
        if value != cas:
            # cas mismatch
            return False
        else:
            # XXX: need "compare and delete" lock flag, potential inconsistency
            # delete the lock flag
            try:
                self.connection.delete(lock_key)
            except pylibmc.Error as e:
                pass
        return True

    def close(self):
        self.connection.disconnect_all()

    def flush(self):
        self.connection.flush_all()

    def stats(self):
        return dict(self.connection.get_stats())
