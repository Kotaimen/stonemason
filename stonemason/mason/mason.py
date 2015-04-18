# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import time
import six

from stonemason.pyramid import TileIndex, MetaTileIndex
from stonemason.tilecache import TileCache, NullTileCache, TileCacheError

from .portrayal import Portrayal
from .builder import create_portrayal_from_theme
from .theme import Theme
from .exceptions import DuplicatedPortrayal


class Mason(object):
    def __init__(self, logger=None):
        self._gallery = dict()
        self._logger = logger

    def load_portrayal_from_theme(self, theme):
        assert isinstance(theme, Theme)

        portrayal = create_portrayal_from_theme(theme)
        if self.has_portrayal(portrayal.name):
            raise DuplicatedPortrayal(portrayal.name)

        self._gallery[portrayal.name] = portrayal

    def get_portrayal(self, name):
        return self._gallery.get(name)

    def put_portrayal(self, name, portrayal):
        assert isinstance(portrayal, Portrayal)
        self._gallery[name] = portrayal

    def has_portrayal(self, name):
        return name in self._gallery

    def __iter__(self):
        return iter(self._gallery)


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
        portrayal = self._mason.get_portrayal(name)
        if portrayal is None:
            return None

        schema = portrayal.get_schema(tag)
        if schema is None:
            return None

        # create metatile index
        stride = portrayal.pyramid.stride
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
            cluster = schema.get_tilecluster(portrayal.bundle,
                                             portrayal.pyramid,
                                             meta_index)
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
        portrayal = self._mason.get_portrayal(name)
        if portrayal is None:
            return None

        schema = portrayal.get_schema(tag)
        if schema is None:
            return None

        # create meta index
        meta_index = MetaTileIndex(z, x, y, stride)

        # render the metatile
        return schema.render_metatile(portrayal.bundle,
                                      portrayal.pyramid,
                                      meta_index)

