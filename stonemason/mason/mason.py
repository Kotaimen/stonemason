# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import time
import six

from stonemason.pyramid import TileIndex, MetaTileIndex
from stonemason.tilecache import TileCache, NullTileCache, TileCacheError

from .mapbook import MapBook
from .builder import create_map_book_from_theme
from .theme import Theme
from .exceptions import DuplicatedMapBook


class MasonMapLibrary(object):
    def __init__(self):
        self._library = dict()

    def load_map_book_from_theme(self, theme):
        assert isinstance(theme, Theme)

        book = create_map_book_from_theme(theme)
        if book.name in self:
            raise DuplicatedMapBook(book.name)

        self[book.name] = book

    def names(self):
        return self._library.keys()

    def books(self):
        return self._library.values()

    def items(self):
        return self._library.items()

    def __getitem__(self, name):
        return self._library[name]

    def __setitem__(self, name, map_book):
        assert isinstance(map_book, MapBook)
        self._library[name] = map_book

    def __contains__(self, name):
        return name in self._library



class Mason(MasonMapLibrary):
    def __init__(self, cache=None, backoff=0.1, logger=None):
        MasonMapLibrary.__init__(self)
        if cache is None:
            cache = NullTileCache()
        assert isinstance(cache, TileCache)
        self._cache = cache
        self._backoff = backoff
        self._logger = logger

    def get_tile(self, name, tag, z, x, y):
        index = TileIndex(z, x, y)

        # get tile from cache
        key = self._make_cache_key(name, tag)

        tile = self._cache.get(key, index)
        if tile is not None:
            # cache hit
            return tile

        # figure out the sheet
        try:
            sheet = self[name][tag]
        except KeyError:
            return None

        # create metatile index
        stride = sheet.pyramid.stride
        meta_index = MetaTileIndex.from_tile_index(index, stride)

        # opportunistic backoff
        if self._backoff:
            lock_index = meta_index.to_tile_index()
            cas = self._cache.lock(key, lock_index)
            if cas == 0:
                # a rendering is already in progress, backoff
                time.sleep(self._backoff)
                # check cache again
                tile = self._cache.get(key, index)
                if tile is not None:
                    return tile
        try:
            # get tile cluster
            cluster = sheet.get_tilecluster(meta_index)
            if cluster is None:
                return None

            # populate cache with tiles in the cluster
            try:
                self._cache.put_multi(key, cluster.tiles)
            except TileCacheError:
                pass
        finally:
            if self._backoff:
                self._cache.unlock(key, lock_index, cas)
        # get tile from the cluster
        tile = cluster[index]

        return tile

    def render_metatile(self, name, tag, z, x, y, stride):
        try:
            sheet = self[name][tag]
        except KeyError:
            return None

        # create meta index
        meta_index = MetaTileIndex(z, x, y, stride)

        # render the metatile
        return sheet.render_metatile(meta_index)


    def _make_cache_key(self, name, tag):
        key = '%s%s' % (name, tag)
        if six.PY2 and isinstance(key, unicode):
            key = key.encode('ascii')
        return key

