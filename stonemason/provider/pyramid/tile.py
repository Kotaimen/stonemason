# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/8/15'

"""
    stonemason.provider.pyramid.tile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Tile and its index.

"""

import collections
import time
import mimetypes

import six

from .serial import Hilbert


class TileIndex(collections.namedtuple('_TileIndex', 'z x y')):
    """ Coordinate index of a map Tile

    Coordinate index of a map Tile using GoogleMaps tile system.

    z:
        zoom level
    x:
        coordinate at longitude axis
    y:
        coordinate at latitude axis
    """

    def __init__(self, z=0, x=0, y=0):
        assert 0 <= x <= 2 ** z
        assert 0 <= y <= 2 ** z

        _TileIndex.__init__(self, z, x, y)

    @property
    def serial(self):
        return Hilbert.coord2serial(*self)

    def __hash__(self):
        return hash(self.serial)

    def __cmp__(self, other):
        return self.serial < other.serial

    def __repr__(self):
        return 'TileIndex(%d/%d/%d)' % self


class Tile(collections.namedtuple('_Tile', 'index data mimetype mtime')):
    """ A Tile
    """
    def __init__(self, index=None, data=None, mimetype=None, mtime=None):
        if index is None:
            index = TileIndex()
        if data is None:
            data = bytes()
        if mimetype is None:
            mimetype = 'application/data'
        if mtime is None:
            mtime = time.time()

        assert isinstance(index, TileIndex)
        assert isinstance(data, bytes)
        _Tile.__init__(self, index, data, mimetype, mtime)


    def __repr__(self):
        return 'Tile(%d/%d/%d)' % self.index

