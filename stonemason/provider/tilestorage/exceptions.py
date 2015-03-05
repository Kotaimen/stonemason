# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/30/15'


class TileStorageError(Exception):
    pass


class InvalidMetaTileIndex(TileStorageError):
    pass


class InvalidMetaTile(TileStorageError):
    pass


class ReadonlyStorage(TileStorageError):
    pass


class TileClusterError(TileStorageError):
    pass

