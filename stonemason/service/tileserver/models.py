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
    def __init__(self, theme_model, cache_servers=None):
        assert isinstance(theme_model, ThemeModel)
        self._theme_model = theme_model
        self._mason = None
        self._cache_servers = cache_servers

    @property
    def mason(self):
        if self._mason is None:
            # lazy initialization
            cache_config = None

            if self._cache_servers is not None:
                cache_servers = re.split(r'[; ]+', self._cache_servers)
                cache_config = dict(
                    prototype='memcache',
                    parameters=dict(servers=cache_servers)
                )

            self._mason = Mason(default_cache_config=cache_config)
            for theme in self._theme_model:
                self._mason.load_theme(theme)

        return self._mason

    def get_tile(self, tag, z, x, y, scale, ext):
        return self.mason.get_tile(tag, z, x, y, scale, ext)

    def get_tile_tags(self):
        return self.mason.get_tile_tags()

#
# class MapModel(object):
# pass
#
#
# class AdminModel(object):
# pass
#
#
# class HealthCheckModel(object):
# pass
