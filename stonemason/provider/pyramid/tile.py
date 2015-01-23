# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/8/15'

"""
    stonemason.provider.pyramid.tile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Square area in a map.

"""

import collections
import time
import mimetypes
import hashlib
import six

from .serial import Hilbert


_TileIndex = collections.namedtuple('_TileIndex', 'z x y')


class TileIndex(_TileIndex):
    """Coordinate of a map Tile.

    Coordinate (aka: index) of a map :class:`~stonemason.provider.pyramid.Tile`
    using GoogleMaps style tile map system.

    `TileIndex` is a `tuple` and thus is immutable once created.


    >>> from stonemason.provider.pyramid import TileIndex
    >>> index = TileIndex(3, 4, 5)
    >>> index
    TileIndex(3/4/5)
    >>> index.z
    3
    >>> index.x
    4
    >>> index.y
    5

    :param z: Zoom level.
    :type z: int
    :param x: Coordinate at x axis.
    :type x: int
    :param y: Coordinate at y axis.
    :type y: int
    """

    def __new__(cls, z=0, x=0, y=0):
        assert z >= 0
        assert 0 <= x < 2 ** z
        assert 0 <= y < 2 ** z
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
    """A piece of square area in a map.

    A `tile` is a piece of square area in a rendered digital map, sliced
    using quad-tree grid system, called :class:`~stonemason.provider.pyramid.Pyramid`.

    Tile is uniquely referenced by its :class:`~stonemason.provider.pyramid.TileIndex`.

    A tile object is immutable once created and has following attributes:

    `index`
        :class:`~stonemason.provider.pyramid.TileIndex`.

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


    Sample:

    >>> from stonemason.provider.pyramid import Tile, TileIndex
    >>> tile = Tile(index=TileIndex(3, 4, 5),
    ...             data=b'a tile',
    ...             mimetype='text/plain',
    ...             mtime=1234.)
    >>> tile
    Tile(3/4/5)
    >>> tile.data
    'a tile'
    >>> tile.mimetype
    'text/plain'
    >>> tile.etag
    'c37ee78cb8b04fa64e295342b3e229cd'


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
            etag = hashlib.md5(data).hexdigest()

        assert isinstance(index, TileIndex)
        assert isinstance(data, bytes)
        assert isinstance(mimetype, six.string_types)
        assert isinstance(mtime, float)
        assert isinstance(etag, six.string_types)

        return _Tile.__new__(cls, index, data, mimetype, mtime, etag)

    def __hash__(self):
        return hash(self.index.serial)

    def __repr__(self):
        return 'Tile(%d/%d/%d)' % self.index

