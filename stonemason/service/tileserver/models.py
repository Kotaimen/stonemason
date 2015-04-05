# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

import re

from stonemason.mason.theme import MemThemeManager, LocalThemeLoader
from stonemason.mason import Mason


class ThemeModel(object):
    def __init__(self, theme_dir):
        theme_loader = LocalThemeLoader(theme_dir)

        self._theme_manager = MemThemeManager()
        theme_loader.load_into(self._theme_manager)

    def __iter__(self):
        return self._theme_manager.iterthemes()

    def get_theme(self, tag):
        return self._theme_manager.get(tag)


class MasonModel(object):
    def __init__(self, themes, cache_servers=None, max_age=300):
        assert isinstance(themes, list)
        self._themes = themes
        self._mason = None
        self._cache_servers = cache_servers
        self._max_age = max_age

    def do_init(self):
        cache_config = None

        if self._cache_servers is not None:
            cache_servers = re.split(r'[; ]+', self._cache_servers)
            cache_config = dict(
                prototype='memcache',
                parameters=dict(servers=cache_servers)
            )

        mason = Mason(cache_config=cache_config, cache_on=True)
        for theme in self._themes:
            mason.load_theme(theme)

        return mason

    @property
    def mason(self):
        if self._mason is None:
            self._mason = self.do_init()

        return self._mason

    def get_tile(self, tag, z, x, y, scale, ext):
        return self.mason.get_tile(tag, z, x, y, scale, ext)

    def get_map(self, tag):
        return self.mason.get_map(tag)

    def get_maps(self):
        return self.mason.get_maps()

    @property
    def cache_control(self):
        if self._max_age == 0:
            return 'max-age=0, nocache'
        else:
            return 'public, max-age=%d' % self._max_age

