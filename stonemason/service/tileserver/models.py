# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from stonemason.mason.theme import MemGallery, FileSystemCurator
from stonemason.mason import Mason, MasonTileVisitor
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
    def __init__(self, themes, cache_servers=None, max_age=300):
        self._mason = None
        self._tile_visitor = None
        self._max_age = max_age
        self._themes = themes

        if cache_servers is not None:
            self._cache = MemTileCache(servers=cache_servers)
        else:
            self._cache = NullTileCache()

    def do_init(self):
        mason = Mason()
        for theme in self._themes:
            mason.load_map_book_from_theme(theme)
        return mason

    @property
    def mason(self):
        if self._mason is None:
            self._mason = self.do_init()
        return self._mason

    @property
    def mason_tile_visitor(self):
        if self._tile_visitor is None:
            self._tile_visitor = MasonTileVisitor(self.mason, self._cache)
        return self._tile_visitor

    @property
    def cache_control(self):
        if self._max_age == 0:
            return 'max-age=0, nocache'
        else:
            return 'public, max-age=%d' % self._max_age

    def get_tile(self, name, tag, z, x, y):
        tile = self.mason_tile_visitor.get_tile(name, tag, z, x, y)
        return tile

    def get_map_book(self, name):
        return self.mason.get_map_book(name)

    def iter_map_books(self):
        return (self.mason.get_map_book(n) for n in self.mason)


