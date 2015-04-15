Tile Cache
**********

.. module:: stonemsaon.tilecache

A `TileCache` temporary stores recently accessed tiles for faster access, or
as a intermediate storage for tiles retrieved from a `TileStorage`.

Only a `memcached` backend is implemented as of now.


Exceptions
==========

.. autoexception:: stonemason.tilecache.TileCacheError
    :members:

.. autoexception:: stonemason.tilecache.MemTileCacheError
    :members:

TileCache
=========

.. autoclass:: stonemason.tilecache.TileCache
   :members:

.. autoclass:: stonemason.tilecache.NullTileCache
   :members:

Memcached
=========

.. autoclass:: stonemason.tilecache.MemTileCache
    :members:




