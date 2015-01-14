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
import hashlib
import six

from .serial import Hilbert


_TileIndex = collections.namedtuple('_TileIndex', 'z x y')


class TileIndex(_TileIndex):
    """ Coordinate of a map Tile.

    Coordinate (aka: index) of a map :class:`~stonemason.provider.pyramid.Tile`
    using GoogleMaps style tile map system.

    .. note::

        `TileIndex` is a `tuple` and thus is immutable once created.


    >>> from stonemason.provider.pyramid import TileIndex
    >>> index = TileIndex(2, 3, 4)
    >>> index.z
    2
    >>> index.x
    3
    >>> index.y
    4

    :param z: Zoom level.
    :type z: int
    :param x: Coordinate at x axis.
    :type x: int
    :param y: Coordinate at y axis.
    :type y: int
    """

    def __new__(cls, z=0, x=0, y=0):
        assert 0 <= x <= 2 ** z
        assert 0 <= y <= 2 ** z
        return _TileIndex.__new__(cls, z, x, y)

    @property
    def serial(self):
        return Hilbert.coord2serial(*self)

    def __hash__(self):
        return hash(self.serial)

    def __repr__(self):
        return 'TileIndex(%d/%d/%d)' % self


_Tile = collections.namedtuple('_Tile', 'index data mimetype mtime etag')


class Tile(_Tile):
    """ A piece of square area in a map.

    A `Tile` is a piece of square area in a rendered digital map, sliced
    using quad-tree grid system, called :class:`~stonemason.provider.pyramid.Pyramid`.

    Tile is uniquely referenced by its :class:`~stonemason.provider.pyramid.TileIndex`.

    A tile object is immutable once created and has following attributes:

    `index`

        Tile index.

    `data`

        Arbitrary binary or textual data, though its usually a rendered
        raster map image, or geo referenced features.

    `mimetype`

        Type of the tile data in mimetypes format, default to
        ``application/data``.  `Tile` will never check whether `mimetype`
        matches actual tile data format.

    `mtime`

        Modify time of the tile since EPOCH in seconds, if its not given in
        the constructor, current time is used by calling :func:`time.time()`


    `etag`

        Hash of the tile data, calculated using class:`hashlib:md5` if is not
        given in the constructor.


    :param index: Tile index.
    :type index: :class:`~stonemason.provider.pyramid.TileIndex`.
    :param data: Tile data.
    :type data: bytes
    :param mimetype: Mimetype of the tile data.
    :type mimetype: str
    :param mtime: Timestamp of the tile.
    :type mtime: float
    :param etag: Hash of the tile data.
    :type etag: bytes
    """

    def __new__(cls, index=None, data=None,
                mimetype=None, mtime=None,
                etag=None):
        if index is None:
            index = TileIndex()
        if data is None:
            data = bytes()
        if mimetype is None:
            mimetype = 'application/data'
        if mtime is None:
            mtime = time.time()
        if etag is None:
            etag = hashlib.md5(data).digest()

        assert isinstance(index, TileIndex)
        assert isinstance(data, bytes)
        assert isinstance(mimetype, six.string_types)
        assert isinstance(mtime, float)
        assert isinstance(etag, six.binary_type)

        return _Tile.__new__(cls, index, data, mimetype, mtime, etag)

    def __hash__(self):
        return hash(self.index.serial)

    def __repr__(self):
        return 'Tile(%d/%d/%d)' % self.index

