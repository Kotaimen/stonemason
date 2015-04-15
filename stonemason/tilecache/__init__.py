# -*- encoding: utf-8 -*-

"""
    stonemason.tilecache
    ~~~~~~~~~~~~~~~~~~~~

    A cache of tiles.
"""

__author__ = 'kotaimen'
__date__ = '12/26/14'

from .tilecache import TileCache, NullTileCache, TileCacheError
from .memcache_ import MemTileCache, MemTileCacheError

