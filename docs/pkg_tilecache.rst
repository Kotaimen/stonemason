Tile Cache
**********

.. module:: stonemsaon.provider.tilecache

A `TileCache` temporary stores recently accessed tiles for faster access, or
as a intermediate storage for tiles retrieved from a `TileStorage`.

Only a `memcached` backend is implemented as of now.


Exceptions
==========

.. autoexception:: stonemason.provider.tilecache.TileCacheError
    :members:

.. autoexception:: stonemason.provider.tilecache.MemTileCacheError
    :members:

TileCache
=========

.. autoclass:: stonemason.provider.tilecache.TileCache
   :members:

.. autoclass:: stonemason.provider.tilecache.NullTileCache
   :members:

Memcached
=========

.. autoclass:: stonemason.provider.tilecache.MemTileCache
    :members:




