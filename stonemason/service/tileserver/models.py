# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

import re

from stonemason.mason.theme import MemThemeManager, LocalThemeLoader
from stonemason.mason import Mason, MapNotFound


class ThemeModel(object):
    def __init__(self, theme_dir):
        theme_loader = LocalThemeLoader(theme_dir)

        self._manager = MemThemeManager()
        theme_loader.load_into(self._manager)

    def get_theme(self, tag):
        return self._manager.get(tag)

    def iter_themes(self):
        return (self._manager.get(k) for k in self._manager)


class MasonModel(object):
    def __init__(self, themes, cache_servers=None, max_age=300):
        self._mason = None
        self._cache_servers = cache_servers
        self._max_age = max_age
        self._themes = themes

    def do_init(self):
        cache_config = None

        if self._cache_servers is not None:
            cache_servers = re.split(r'[; ]+', self._cache_servers)
            cache_config = dict(servers=cache_servers)

        mason = Mason(cache_config=cache_config)
        for theme in self._themes:
            mason.load_map_from_theme(theme)

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

    def get_tile(self, name, z, x, y, scale, ext):
        try:
            return self.mason.get_tile(name, z, x, y)
        except MapNotFound:
            return None

    def get_map(self, tag):
        try:
            return self.mason.get_map(tag)
        except MapNotFound:
            return None

    def iter_maps(self):
        return (self.mason.get_map(k) for k in self.mason)


