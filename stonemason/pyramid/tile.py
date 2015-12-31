# -*- encoding: utf-8 -*-

"""
    stonemason.pyramid.tile
    ~~~~~~~~~~~~~~~~~~~~~~~
    Square area in a map.

"""
__author__ = 'kotaimen'
__date__ = '1/8/15'

import collections
import time
import hashlib

import six

from stonemason.pyramid.serial import Hilbert


_TileIndex = collections.namedtuple('_TileIndex', 'z x y')


class TileIndex(_TileIndex):
    """Coordinate uniquely reference a map :class:`~stonemason.pyramid.Tile`.

    `TileIndex` is a `tuple` and thus is immutable once created.

    >>> from stonemason.pyramid import TileIndex
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
    """A piece of square area in a map, sliced using quad-tree grid coverage
    model.

    Tile is uniquely referenced by its :class:`~stonemason.pyramid.TileIndex`.

    A tile object is immutable once created.

    >>> from stonemason.pyramid import Tile, TileIndex
    >>> tile = Tile(index=TileIndex(3, 4, 5),
    ...             data=b'a tile',
    ...             mimetype='text/plain',
    ...             mtime=1234.)
    >>> tile
    Tile(3/4/5)
    >>> tile.data
    b'a tile'
    >>> tile.mimetype
    'text/plain'
    >>> tile.etag
    'c37ee78cb8b04fa64e295342b3e229cd'

    :param index: Index of the tile.
    :type index: :class:`~stonemason.pyramid.TileIndex`.

    :param data: Arbitrary binary or textual data, though its usually
        a rendered raster map image, or geo referenced features.
    :type data: bytes

    :param mimetype: Type of the tile data in mimetypes format, default to
        :mimetype:`application/data`.  Note `Tile` will never check whether
        `mimetype` matches actual tile data format.
    :type mimetype: str

    :param mtime: Modify time of the tile since EPOCH in seconds, if it is
        not given, current time is used by calling :func:`time.time()`
    :type mtime: float

    :param etag: Hash of the tile data, calculated using :class:`hashlib:md5`
        if is not given.
    :type etag: str

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

