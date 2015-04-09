Tile Map System
***************

.. module::stonemason.pyramid
.. module::stonemason.pyramid.geo

Module :mod:`stonemason.pyramid` defines the tile map coverage model and tile
data schema.

Pyramid
=======

.. autoclass:: stonemason.pyramid.Pyramid
    :members:

Tile
====

.. autoclass:: stonemason.pyramid.TileIndex
    :members:

.. autoclass:: stonemason.pyramid.Tile
    :members:


MetaTile
========

.. autoclass:: stonemason.pyramid.MetaTileIndex
    :members:

.. autoclass:: stonemason.pyramid.MetaTile
    :members:


Hilbert Curve
=============

.. function:: stonemason.util.geo.hilbert.hil_xy_from_s(s, n)

    Compute point coordinate from given Hilbert curve length.

    Given the order `n` of a Hilbert curve, compute point coordinate `(x, y)`
    using length `n`.  This is the reverse operation of :func:`hil_s_from_xy`

        >>> from stonemason.pyramid import hil_xy_from_s
        >>> hil_xy_from_s(10, 2)
        (3L, 3L)
        >>> hil_xy_from_s(829371542099833, 25)
        (31152875L, 17840406L)

    :param s: Length of the Hilbert curve.
    :param n: Order of the Hilbert curve
    :return: Coordinate as a tuple `(x, y)`.
    :rtype: tuple

.. function:: stonemason.util.geo.hilbert.hil_s_from_xy(x, y, n)

    Compute Hilbert curve length from given point coordinate.

    Given the order `n` of a Hilbert curve and coordinates `x` and `y`,
    computes the length `s` of the curve from the origin to `(x, y)`.

        >>> from stonemason.pyramid import hil_s_from_xy
        >>> hil_s_from_xy(3,3, 2)
        10L
        >>> hil_s_from_xy(31152875, 17840406, 25)
        829371542099833L

    :param x: x coordinate.
    :param y: y coordinate.
    :param n: Order of the Hilbert curve.
    :type n: int
    :return: Hilbert curve length.
    :rtype: int


Sequential Enumeration
======================

.. autoclass:: stonemason.pyramid.Hilbert
    :members:

.. autoclass:: stonemason.pyramid.Legacy
    :members:


Coverage Model
==============

.. autodata:: stonemason.pyramid.geo.HAS_GDAL
    :annotation:

.. autoclass:: stonemason.pyramid.geo.TileMapSystem
    :members:
