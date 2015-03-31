# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

from stonemason.provider.tileprovider import TileProvider


class MasonMap(object):
    def __init__(self, name, metadata, provider):
        assert isinstance(metadata, dict)
        assert isinstance(provider, TileProvider)
        self._name = name
        self._metadata = metadata
        self._provider = provider

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    @property
    def provider(self):
        return self._provider
