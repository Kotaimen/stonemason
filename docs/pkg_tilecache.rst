Tile Cache
**********

.. module:: stonemsaon.provider.tilecache

A `TileCache` temporary stores recently accessed tiles for faster access, or
as a intermediate storage when metatile or tilecluster is retrieved from a
TileStorage.

TileCache has no persistence and depends on a distributed cache.

Currently there is only a `memcached` cache.


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




