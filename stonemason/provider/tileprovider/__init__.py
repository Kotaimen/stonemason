# -*- encoding: utf-8 -*-
"""
    stonemason.provider.tileprovider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    A Tile Provider provides tile from a given cache or storage.

"""

__author__ = 'kotaimen'
__date__ = '1/5/15'

from .provider import TileProvider, NullTileProvider
from .storage import StorageTileProvider
from .renderer import RendererTileProvider
from .hybrid import HybridTileProvider

