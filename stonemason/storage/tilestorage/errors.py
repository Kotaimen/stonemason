# -*- encoding: utf-8 -*-
"""
    stonemason.storage.tilestorage.errors
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Exceptions for tile storage module.
"""
__author__ = 'ray'
__date__ = '10/26/15'

from ..concept import StorageError


class MetaTileStorageError(StorageError):
    """Base MetaTile Storage Error

    The base class for all metatile storage exceptions.
    """
    pass


class ReadonlyStorage(MetaTileStorageError):
    """Read Only Storage

    Raise when trying to modify a read only storage.
    """
    pass


class InvalidMetaTileIndex(MetaTileStorageError):
    """Invalid MetaTile Index

    Raise when metatile index is not valid.
    """
    pass


class InvalidMetaTile(MetaTileStorageError):
    """Invalid MetaTile

    Raise when metatile is not valid.
    """
    pass
