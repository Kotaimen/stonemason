# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/30/15'


class DictTheme(object):
    def __init__(self, **config):
        self._config = config

    def get_attribute(self, key, default=None):
        return self._config.get(key, default)

    def __repr__(self):
        return repr(self._config)


class TileMatrixTheme(DictTheme):
    @property
    def tag(self):
        return self.get_attribute('tag')

    @property
    def maptype(self):
        return self.get_attribute('maptype')

    @property
    def tileformat(self):
        return self.get_attribute('tileformat')

    @property
    def pyramid(self):
        return self.get_attribute('pyramid')

    @property
    def storage(self):
        return self.get_attribute('storage')

    @property
    def renderer(self):
        return self.get_attribute('renderer')


class Theme(DictTheme):
    @property
    def name(self):
        return self.get_attribute('name')

    @property
    def metadata(self):
        return self.get_attribute('metadata')

    @property
    def maptype(self):
        return self.get_attribute('maptype')

    @property
    def tileformat(self):
        return self.get_attribute('tileformat')

    @property
    def pyramid(self):
        return self.get_attribute('pyramid')

    @property
    def tilematrix_set(self):
        for matrix in self.get_attribute('tilematrix_set', default=list()):
            yield TileMatrixTheme(**matrix)

