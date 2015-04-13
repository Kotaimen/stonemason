# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

from stonemason.pyramid import TileIndex, MetaTileIndex
from stonemason.provider.tilecache import TileCache, NullTileCache
from stonemason.provider.tilestorage import MetaTileStorage, NullMetaTileStorage

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
    def __init__(self, mason, cache=None):
        if cache is None:
            cache = NullTileCache()
        assert isinstance(mason, Mason)
        assert isinstance(cache, TileCache)
        self._mason = mason
        self._cache = cache

    def get_tile(self, name, tag, z, x, y):
        index = TileIndex(z, x, y)

        # get tile from cache
        key = self._make_cache_key(name, tag)
        tile = self._cache.get(key, index)
        if tile is not None:
            # cache hit
            return tile

        portrayal = self._mason.get_portrayal(name)
        if portrayal is None:
            return None

        tilematrix = portrayal.get_tilematrix(tag)
        if tilematrix is None:
            return None

        # create meta index
        stride = portrayal.pyramid.stride
        meta_index = MetaTileIndex.from_tile_index(index, stride)

        # get tile cluster
        cluster = tilematrix.get_tilecluster(
            portrayal.bundle, portrayal.pyramid, meta_index)
        if cluster is None:
            return None

        # populate cache with tiles in the cluster
        self._cache.put_multi(key, cluster.tiles)

        # get tile from the cluster
        tile = cluster[index]

        return tile

    def _make_cache_key(self, name, tag):
        return '%s-%s' % (name, tag)


class MasonMetaTileFarm(object):
    def __init__(self, mason, storage=None):
        if storage is None:
            storage = NullMetaTileStorage()
        assert isinstance(mason, Mason)
        assert isinstance(storage, MetaTileStorage)
        self._mason = mason
        self._storage = storage

    def render_metatile(self, name, tag, z, x, y, stride):
        portrayal = self._mason.get_portrayal(name)
        if portrayal is None:
            return None

        tilematrix = portrayal.get_tilematrix(tag)
        if tilematrix is None:
            return None

        # create meta index
        meta_index = MetaTileIndex(z, x, y, stride)

        # get tile cluster
        metatile = tilematrix.get_metatile(
            portrayal.bundle, portrayal.pyramid, meta_index)
        if metatile is None:
            return False

        self._storage.put(metatile)

        return True

