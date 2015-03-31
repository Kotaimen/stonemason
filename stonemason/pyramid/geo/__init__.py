# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/20/15'

try:
    from .tms import TileMapError, TileMapSystem, Envelope
except ImportError:
    TileMapError = None
    TileMapSystem = None
    Envelope = None
