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


class Mason(object):
    def __init__(self, logger=None):
        self._library = dict()
        self._logger = logger

    def load_map_book_from_theme(self, theme):
        assert isinstance(theme, Theme)

        book = create_map_book_from_theme(theme)
        if self.has_map_book(book.name):
            raise DuplicatedMapBook(book.name)

        self._library[book.name] = book

    def get_map_book(self, name):
        return self._library.get(name)

    def put_map_book(self, name, map_book):
        assert isinstance(map_book, MapBook)
        self._library[name] = map_book

    def has_map_book(self, name):
        return name in self._library

    def __iter__(self):
        return iter(self._library)


class MasonTileVisitor(object):
    def __init__(self, mason, cache=None, backoff=0.1):
        if cache is None:
            cache = NullTileCache()
        assert isinstance(mason, Mason)
        assert isinstance(cache, TileCache)
        self._mason = mason
        self._cache = cache
        self._backoff = backoff

    def get_tile(self, name, tag, z, x, y):
        index = TileIndex(z, x, y)

        # get tile from cache
        key = self._make_cache_key(name, tag)
        tile = self._cache.get(key, index)
        if tile is not None:
            # cache hit
            return tile

        # figure out theme and schema tile belongs to
        book = self._mason.get_map_book(name)
        if book is None:
            return None

        sheet = book[tag]
        if sheet is None:
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

    def _make_cache_key(self, name, tag):
        key = '%s%s' % (name, tag)
        if six.PY2 and isinstance(key, unicode):
            key = key.encode('ascii')
        return key


class MasonMetaTileFarm(object):
    def __init__(self, mason):
        assert isinstance(mason, Mason)
        self._mason = mason

    def render_metatile(self, name, tag, z, x, y, stride):
        book = self._mason.get_map_book(name)
        if book is None:
            return None

        sheet = book[tag]
        if sheet is None:
            return None

        # create meta index
        meta_index = MetaTileIndex(z, x, y, stride)

        # render the metatile
        return sheet.render_metatile(meta_index)

