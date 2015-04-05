# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/30/15'

from functools import reduce


class DictTheme(object):
    def __init__(self, **config):
        self._config = config

    def get_attribute(self, key_list, default=None):
        try:
            return reduce(lambda d, k: d[k], key_list, self._config)
        except KeyError:
            return default

    def put_attribute(self, key_list, val):
        self.get_attribute(key_list[:-1])[key_list[-1]] = val


class MapTheme(DictTheme):
    THEME_NAME = ['name']

    THEME_METADATA = ['metadata']

    THEME_PYRAMID = ['provider', 'pyramid']

    THEME_MAPTYPE = ['provider', 'maptype']

    THEME_TILEFORMAT = ['provider', 'tileformat']

    THEME_STORAGE = ['provider', 'storage']

    THEME_RENDERER = ['provider', 'renderer']

    def __init__(self, **config):
        DictTheme.__init__(self, **config)

        self._name = self.get_attribute(
            self.THEME_NAME, '')

        self._metadata = self.get_attribute(
            self.THEME_METADATA, dict())

        self._pyramid = self.get_attribute(
            self.THEME_PYRAMID, dict())

        self._maptype = self.get_attribute(
            self.THEME_MAPTYPE, 'image')

        self._tileformat = self.get_attribute(
            self.THEME_TILEFORMAT, {'format': 'PNG'})

        self._storage = self.get_attribute(
            self.THEME_STORAGE, {'prototype': 'null'})

        self._renderer = self.get_attribute(
            self.THEME_RENDERER, {'prototype': 'null'})

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    @property
    def pyramid(self):
        return self._pyramid

    @property
    def maptype(self):
        return self._maptype

    @property
    def tileformat(self):
        return self._tileformat

    @property
    def storage(self):
        return self._storage

    @property
    def renderer(self):
        return self._renderer
