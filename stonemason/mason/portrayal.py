# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import FormatBundle

from .metadata import Metadata
from .tilematrix import TileMatrix


class Portrayal(object):
    def __init__(self, name, metadata, bundle, pyramid, matrix_set=None):
        if matrix_set is None:
            matrix_set = dict()
        assert isinstance(metadata, Metadata)
        assert isinstance(bundle, FormatBundle)
        assert isinstance(pyramid, Pyramid)
        assert isinstance(matrix_set, dict)
        self._name = name
        self._metadata = metadata
        self._bundle = bundle
        self._pyramid = pyramid
        self._matrix_set = matrix_set

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    @property
    def bundle(self):
        return self._bundle

    @property
    def pyramid(self):
        return self._pyramid

    def put_tilematrix(self, tag, tilematrix):
        assert isinstance(tilematrix, TileMatrix)
        self._matrix_set[tag] = tilematrix

    def get_tilematrix(self, tag):
        return self._matrix_set.get(tag)

    def has_tilematrix(self, tag):
        return tag in self._matrix_set

    def iter_tilematrix(self):
        return iter(self._matrix_set)

