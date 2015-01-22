Tile Cache
==========

A `TileCache` temporary stores recently accessed tiles for faster access, or
as a intermediate storage when metatile or tilecluster is retrieved from a
TileStorage.

TileCache has no persistence and depends on a distributed cache.

Currently there is only `memcached` cache.
The interface `TileCache` class can be used as a *null* cache.

Exception
---------

.. autoclass:: stonemason.provider.tilecache.TileCacheError
    :members:

TileCache
---------

.. autoclass:: stonemason.provider.tilecache.TileCache
   :members:

.. autoclass:: stonemason.provider.tilecache.NullTileCache
   :members:

Memcached
---------

.. autoclass:: stonemason.provider.tilecache.MemTileCache
    :members:




