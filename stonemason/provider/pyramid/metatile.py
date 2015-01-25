# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/18/15'

"""
    stonemason.provider.pyramid.metatile
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Large square area in a map.
"""

import collections
import time
import hashlib

import six

from .tile import Tile, TileIndex
from .serial import Hilbert

_MetaTileIndex = collections.namedtuple('_MetaTileIndex', 'z x y stride')


class MetaTileIndex(_MetaTileIndex):
    """Coordinate of a `metatile`.

    A `metatile` is always indexed by its left top tile, the constructor will
    snap coordinate to left top tile if other tile index is given.

    `stride` must be order of 2, if specified stride makes metatile larger
    than current zoom level, it will be rounded down to level size.

    `MetaTileIndex` is a `tuple` and thus is immutable once created.

    >>> from stonemason.provider.pyramid import MetaTileIndex, TileIndex
    >>> index = MetaTileIndex(2, 0, 0, 2)
    >>> index
    MetaTileIndex(2/0/0@2)
    >>> list(index.fission())
    [TileIndex(2/0/0), TileIndex(2/0/1), TileIndex(2/1/0), TileIndex(2/1/1)]
    >>> MetaTileIndex(2, 0, 0, 8)
    MetaTileIndex(2/0/0@4)
    >>> MetaTileIndex(8, 11, 7, 8)
    MetaTileIndex(8/8/0@8)

    :param z: z zoom level
    :type z: int
    :param x: x coordinate
    :type x: int
    :param y: y coordinate
    :type y: int
    :param stride: number of `tiles` per axis
    :type stride: int
    """

    def __new__(cls, z=0, x=0, y=0, stride=1):
        # must be power of 2
        assert stride & ( stride - 1 ) == 0
        assert z >= 0
        dim = 2 ** z
        # check axis range
        assert 0 <= x < dim
        assert 0 <= y < dim

        # round coordinate to left top tile in the meta tile
        x -= (x % stride)
        y -= (y % stride)

        # adjust if stride is too large for current layer
        if (stride >> z) > 0:
            stride = dim

        return _MetaTileIndex.__new__(cls, z, x, y, stride)

    def __hash__(self):
        return Hilbert.coord2serial(*self)

    def fission(self):
        """Fission the `MetaTileIndex` into `TileIndexes`.

        Return a iterable of :class:`~stonemason.provider.pyramid.TileIndex`
        of all the tiles covered by this metatile.

        :return: :class:`~stonemason.provider.pyramid.TileIndex`
        """
        z, x, y, stride = self
        for xi in range(x, x + stride):
            for yi in range(y, y + stride):
                yield TileIndex(z, xi, yi)

    def __repr__(self):
        return 'MetaTileIndex(%d/%d/%d@%d)' % self


_MetaTile = collections.namedtuple('_MetaTile',
                                   'index data mimetype mtime etag buffer')


class MetaTile(_MetaTile):
    """Large piece of square area in a map.

    A `metatile` uses same quad-tree grid as a tile but the grid is sparser,
    thus single metatile covers same area of :math:`stride^2` tiles.

    Group tiles into metatile greatly reduces number of operations,
    so metatile is the basic unit of storage and map rendering.

    `index`
        Index of the metatile.

    `data`
        Arbitrary binary or textual data.

    `mimetype`
        Type of the metatile data in mimetypes format, default to
        ``application/data``.

    `mtime`
        Modify time of the metatile since EPOCH in seconds.

    `etag`
        Hash of the metatile data.

    `buffer`
        Size of extra pixels around the metatile, only meaningful for raster
        image metatiles, default is `0`, which means no buffering.

    >>> from stonemason.provider.pyramid import MetaTileIndex, MetaTile
    >>> metatile = MetaTile(MetaTileIndex(2, 0, 0, 2),
    ...                     data=b'a metatile',
    ...                     mimetype='text/plain',
    ...                     mtime=1234.,
    ...                     buffer=16)
    >>> metatile
    MetaTile(2/0/0@2)
    >>> metatile.buffer
    16

    :param index: Metatile index.
    :type index: :class:`~stonemason.provider.pyramid.MetaTileIndex`.
    :param data: Tile data.
    :type data: bytes
    :param mimetype: Mimetype of the metatile data.
    :type mimetype: str
    :param mtime: Timestamp of the metatile.
    :type mtime: float
    :param etag: Hash of the metatile data.
    :type etag: bytes
    :param buffer: Pixel size of buffer around the metatile.
    :type buffer: int
    """

    def __new__(cls, index=None, data=None,
                mimetype=None, mtime=None, etag=None,
                buffer=0):

        if index is None:
            index = MetaTileIndex()

        if data is None:
            data = bytes()

        if mimetype is None:
            mimetype = 'application/data'

        if mtime is None:
            mtime = time.time()

        if etag is None:
            etag = hashlib.md5(data).hexdigest()

        assert isinstance(index, MetaTileIndex)
        assert isinstance(data, bytes)
        assert isinstance(mimetype, six.string_types)
        assert isinstance(mtime, float)
        assert isinstance(etag, six.string_types)
        assert isinstance(buffer, int) and buffer >= 0

        return _MetaTile.__new__(cls, index, data, mimetype, mtime,
                                 etag, buffer)

    def __repr__(self):
        return 'MetaTile(%d/%d/%d@%d)' % self.index
