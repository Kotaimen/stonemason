# -*- encoding: utf-8 -*-
"""
    stonemason.mason.mason
    ~~~~~~~~~~~~~~~~~~~~~~
    Facade of StoneMason.

"""

import six

from stonemason.pyramid import TileIndex, MetaTileIndex
from stonemason.provider.tilecache import NullTileCache, MemTileCache

from .masonmap import MasonMap
from .mapbuilder import MapBuilder
from .exceptions import MapNotFound, DuplicatedMap


class Mason(object):
    def __init__(self, logger=None, cache_config=None):
        self._gallery = dict()
        self._logger = logger

        # create cache
        if cache_config is not None:
            assert isinstance(cache_config, dict)
            self._cache = MemTileCache(**cache_config)
        else:
            self._cache = NullTileCache()

    def load_map_from_theme(self, theme):
        mason_map = MapBuilder().build_from_theme(theme)
        self.put_map(mason_map.name, mason_map)

    def has_map(self, name):
        return name in self._gallery

    def put_map(self, name, mason_map):
        assert isinstance(mason_map, MasonMap)
        if self.has_map(name):
            raise DuplicatedMap(name)
        self._gallery[name] = mason_map

    def get_map(self, name):
        try:
            return self._gallery[name]
        except KeyError:
            raise MapNotFound(name)

    def get_tile(self, name, z, x, y):
        mason_map = self.get_map(name)

        tag = mason_map.name

        index = TileIndex(z, x, y)

        # get tile from cache
        tile = self._cache.get(tag, index)
        if tile is not None:
            # cache hit
            return tile

        # create meta index
        stride = mason_map.provider.pyramid.stride
        meta_index = MetaTileIndex.from_tile_index(index, stride)

        # get tile cluster
        cluster = mason_map.provider.get_tilecluster(meta_index)
        if cluster is None:
            return None

        # populate cache with tiles in the cluster
        self._cache.put_multi(tag, cluster.tiles)

        # get tile from the cluster
        tile = cluster[index]

        return tile

    def __iter__(self):
        return iter(self._gallery)
