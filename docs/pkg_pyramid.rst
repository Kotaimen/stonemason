Tile System
===========

.. module::stonemason.provider.pyramid

:mod:`stonemason.provider.pyramid` contains definitions of `tile`, `metatile`
and the quad tree `pyramid`.

All classes in this package is implemented using :func:`collections.namedtuple`
thus is immutable and pickle serializable.

Tile
----

.. autoclass:: stonemason.provider.pyramid.TileIndex
    :members:

.. autoclass:: stonemason.provider.pyramid.Tile
    :members:


MetaTile
--------

.. autoclass:: stonemason.provider.pyramid.MetaTileIndex
    :members:

.. autoclass:: stonemason.provider.pyramid.MetaTile
    :members:

Serial
------

.. autoclass:: stonemason.provider.pyramid.Hilbert
    :members:

.. autoclass:: stonemason.provider.pyramid.Legacy
    :members:


Pyramid
-------

.. autoclass:: stonemason.provider.pyramid.Pyramid
    :members:
