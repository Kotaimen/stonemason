Tile System
***********

.. module::stonemason.pyramid

:mod:`stonemason.pyramid` contains definitions of `tile`, `metatile`
and the quad tree `pyramid`.

All classes in this package is implemented using :func:`collections.namedtuple`
thus is immutable and pickle serializable.

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

Serial
======

.. autoclass:: stonemason.pyramid.Hilbert
    :members:

.. autoclass:: stonemason.pyramid.Legacy
    :members:

