# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/12/15'

"""
    stonemason.provider.tilecache.memcache_
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Memcached tile cache
"""

import re
import json
import pylibmc

from .tilecache import TileCache, TileCacheError
from stonemason.provider.pyramid import Tile, TileIndex


class MemTileCache(TileCache):
    """A tile cache based on `memcached` protocol backend.

    .. Note::

        `memcached` has a limit on cache object size, usually its ``4MB``.

    Tile cache based on `memcached`_ protocol backend using `pylibmc`_ driver.
    The backend does not necessary being `memcached` itself, any storage or
    proxy talks its protocol will work, like `couchbase`_ or `nutcracker`_.

    .. _memcached: <http://memcached.org/>
    .. _pylibmc: <http://sendapatch.se/projects/pylibmc/>
    .. _couchbase: <http://www.couchbase.com/>
    .. _nutcracker:  <https://github.com/twitter/twemproxy>

    `servers`

        A list of servers, the list is sent to :class:`pylibmc.Client`, default
        value is ``['localhost:11211',]``.

        .. seealso:: `pylibmc` `example <http://sendapatch.se/projects/pylibmc/index.html>`_.

    `behaviors`

        Set `pylibmc` client behaviours, default is ``{'tcp_nodelay': True, 'ketama': True}``.

        .. seealso:: `pylibmc` `behaviours <http://sendapatch.se/projects/pylibmc/behaviors.html>`_.

    :param servers: A sequence of strings specifying the servers to use.
    :param binary: Whether to use `memcached` binary protocol, default is ``False``.
    :param behaviors: `pylibmc` behaviors.
    """

    def __init__(self, servers=('localhost:11211', ), binary=False,
                 behaviors=None):
        super(TileCache, self).__init__()
        if behaviors is None:
            behaviors = {'tcp_nodelay': True,
                         'ketama': True}
        self.connection = pylibmc.Client(servers, binary=binary,
                                         behaviors=behaviors)
        # Verify connection
        self.connection.get_stats()


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
        values = self.connection.get_multi([key, metadata_key])

        try:
            data = values[key]
            metadata = values[metadata_key]
        except KeyError:
            # only successful when both keys are retrieved
            return None

        try:
            mimetype, mtime, etag = self._load_metadata(metadata)
        except ValueError:
            raise TileCacheError('Invalid metadata: "%s"' % metadata_key)

        return Tile(index, data, mimetype, mtime, etag)

    def put(self, tag, tile, ttl=0):
        key, metadata_key, _ = self._make_key(tag, tile.index)
        metadata = self._make_metadata(tile)
        data = {key: tile.data,
                metadata_key: metadata}

        failed = self.connection.set_multi(data, time=ttl)
        if len(failed) > 0:
            raise TileCacheError('Tile not successfully writen: "%s"' % failed)

    def has(self, tag, index):
        key, _, _ = self._make_key(tag, index)

        return self.connection.touch(key)

    def retire(self, tag, index):
        key, metadata_key, _ = self._make_key(tag, index)

        self.connection.delete_multi([key, metadata_key])

    def put_multi(self, tag, tiles, ttl=0):
        data = {}
        for tile in tiles:
            key, metadata_key, _ = self._make_key(tag, tile.index)
            data[key] = tile.data
            data[metadata_key] = self._make_metadata(tile)

        failed = self.connection.set_multi(data, time=ttl)
        if len(failed) > 0:
            raise TileCacheError('Tile not successfully writen: "%s"' % failed)

    def close(self):
        self.connection.disconnect_all()

    def flush(self):
        self.connection.flush_all()
