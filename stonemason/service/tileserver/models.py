# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from stonemason.mason.theme import MemGallery, FileSystemCurator
from stonemason.mason import Mason
from stonemason.tilecache import MemTileCache, NullTileCache


class ThemeModel(object):
    def __init__(self, theme_dir):
        theme_loader = FileSystemCurator(theme_dir)

        self._gallery = MemGallery()
        theme_loader.add_to(self._gallery)

    def get_theme(self, name):
        return self._gallery.get(name)

    def put_theme(self, name, theme):
        self._gallery.put(name, theme)

    def iter_themes(self):
        return (self._gallery.get(n) for n in self._gallery)


class MasonModel(object):
    def __init__(self, themes, cache_servers=None, max_age=300, readonly=False):
        self._mason = None
        self._tile_visitor = None
        self._max_age = max_age
        self._themes = themes
        self._readonly = readonly

        if cache_servers is not None:
            self._cache = MemTileCache(servers=cache_servers)
        else:
            self._cache = NullTileCache()

    def do_init(self):
        mason = Mason(cache=self._cache, readonly=self._readonly)
        for theme in self._themes:
            mason.load_map_book_from_theme(theme)
        return mason

    @property
    def mason(self):
        if self._mason is None:
            self._mason = self.do_init()
        return self._mason

    @property
    def cache_control(self):
        if self._max_age == 0:
            return 'max-age=0, nocache'
        else:
            return 'public, max-age=%d' % self._max_age
