# -*- encoding: utf-8 -*-
"""
    stonemason.mason.mason
    ~~~~~~~~~~~~~~~~~~~~~~
    Facade of StoneMason.

"""

import six

from stonemason.pyramid import TileIndex, MetaTileIndex
from stonemason.provider.tilecache import NullTileCache, MemTileCache

from .mapbuilder import MapBuilder
from .exceptions import DuplicatedMapError


class Mason(object):
    """Stonemason Facade

    `Mason` is the facade of `Stonemason`. A `Mason` object provides tiles of
    various kinds of themes from caches, storage and renders.

    Themes could be loaded or unloaded by their names. Though, these with
    duplicated names are not allowed.

    In `Mason`, tiles are served according to their tags which, for now,
    equals to the name of their themes.

    :param theme_store: A `ThemeManager` instance that contains piles of themes.
    :type theme_store: :class:`stonemason.mason.theme.ThemeManager`

    :param readonly: A bool variable that controls serving mode of `Mason`.
    :type readonly: bool

    """

    def __init__(self,
                 readonly=False,
                 logger=None,
                 cache_config=None,
                 cache_on=True):
        assert isinstance(readonly, bool)

        self._logger = logger
        self._readonly = readonly
        self._cache_on = cache_on

        if cache_config is None:
            self._cache = NullTileCache()
        else:
            self._cache = MemTileCache(cache_config.get('parameters', dict()))

        self._maps = dict()

    def load_theme(self, theme):
        """Load the named theme"""
        mason_map = MapBuilder().build_from_theme(theme)
        if mason_map.name in self._maps:
            raise DuplicatedMapError('Map already exists "%s"' % mason_map.name)

        self._maps[mason_map.name] = mason_map

    def get_map(self, tag):
        try:
            mason_map = self._maps[tag]
        except KeyError:
            return None
        return mason_map

    def get_maps(self):
        """Get all available tile tags"""
        return self._maps

    def get_tile(self, tag, z, x, y, scale, ext):
        """Get a tile with the given tag and parameters"""

        mason_map = self.get_map(tag)
        if mason_map is None:
            return None

        index = TileIndex(z, x, y)

        if self._cache_on:
            tile = self._cache.get(mason_map.name, index)
            if tile is not None:
                return tile

        meta_index = MetaTileIndex.from_tile_index(
            index, mason_map.provider.pyramid.stride)

        cluster = mason_map.provider.get_tilecluster(meta_index)
        if cluster is None:  # cluster miss
            return None

        if self._cache_on:
            self._cache.put_multi(mason_map.name, cluster.tiles)

        # cluster hit
        tile = cluster[index]

        return tile
