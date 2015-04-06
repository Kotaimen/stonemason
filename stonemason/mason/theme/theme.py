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
    DEFAULT = {
        'name': '',
        'metadata': {},
        'provider': {
            'maptype': 'image',
            'tileformat': {'format': 'PNG'},
            'pyramid': {},
            'storage': {'prototype': 'null'},
            'renderer': {'prototype': 'null'}
        }

    }

    @property
    def name(self):
        return self.get_attribute(
            ['name'], self.DEFAULT['name'])

    @property
    def metadata(self):
        return self.get_attribute(
            ['metadata'], self.DEFAULT['metadata'])

    @property
    def maptype(self):
        return self.get_attribute(
            ['provider', 'maptype'], self.DEFAULT['provider']['maptype'])

    @property
    def tileformat(self):
        return self.get_attribute(
            ['provider', 'tileformat'], self.DEFAULT['provider']['tileformat'])

    @property
    def pyramid(self):
        return self.get_attribute(
            ['provider', 'pyramid'], self.DEFAULT['provider']['pyramid'])

    @property
    def storage(self):
        return self.get_attribute(
            ['provider', 'storage'], self.DEFAULT['provider']['storage'])

    @property
    def renderer(self):
        return self.get_attribute(
            ['provider', 'renderer'], self.DEFAULT['provider']['renderer'])
