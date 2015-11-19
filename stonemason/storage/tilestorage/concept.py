# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/19/15'

import six
from stonemason.pyramid import MetaTileIndex, MetaTile
from stonemason.storage.concept import StorageError, StorageKeyConcept, \
    ObjectSerializeConcept, GenericStorageConcept


class MetaTileStorageError(StorageError):
    """Base MetaTile Storage Error

    The base class for all metatile storage exceptions.
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


class ReadOnlyMetaTileStorage(MetaTileStorageError):
    """Read Only Storage

    Raise when storage is read only.
    """
    pass


class MetaTileKeyConcept(StorageKeyConcept):  # pragma: no cover
    """MetaTile Key Concept

    Basic class for MetaTile key mode. A MetaTile key mode maps a MetaTile index
    into a literal string.

    :param prefix: Prefix of the key string.
    :type prefix: str

    :param extension: Suffix of the key string.
    :type extension: str

    :param sep: The character used to separate key components.
    :type sep: str

    :param gzip: If append .gz after extension.
    :type gzip: bool

    """

    def __init__(self, prefix='', extension='.png', sep='/', gzip=False):
        assert isinstance(prefix, six.string_types)
        assert extension.startswith('.')
        self._prefix = prefix
        self._extension = extension
        self._sep = sep

        if gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'


class MetaTileSerializeConcept(ObjectSerializeConcept):  # pragma: no cover
    """MetaTile Serializer Concept"""
    pass


# ==============================================================================
# MetaTile Storage
# ==============================================================================
class MetaTileStorageConcept(object):
    """MetaTile Storage Concept

    The ``MetaTileStorageConcept`` defines basic interfaces of a MetaTile
    storage.

    """

    @property
    def levels(self):
        """Metatile levels in the storage.

        :return: The level limits of the stored MetaTile.
        :rtype: list

        """
        raise NotImplementedError

    @property
    def stride(self):
        """Stride of metatiles in the storage

        :return: The stride of the stored MetaTile.
        :rtype: int

        """
        raise NotImplementedError

    def has(self, index):
        """ Check whether given index exists in the storage.

        :param index: MetaTile index.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`

        :return: Whether the metatile exists.
        :rtype: bool

        """
        raise NotImplementedError

    def get(self, index):
        """Retrieve a `MetaTile` from the storage.

        Retrieve a `MetaTile` from the storage, returns ``None`` if not found.

        :param index: MetaTile index of the MetaTile.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`

        :returns: Retrieved tile cluster.
        :rtype: :class:`~stonemason.tilestorage.MetaTile` or ``None``

        """
        raise NotImplementedError

    def put(self, metatile):
        """Store a `MetaTile` in the storage.

        Store a `MetaTile` in the storage, overriding any existing one.

        :param metatile: The MetaTile to store.
        :type metatile: :class:`~stonemason.pyramid.MetaTile`

        """
        raise NotImplementedError

    def retire(self, index):
        """Delete `MetaTile` with given index.

        If `MetaTile` does not present in cache, this operation has no effect.

        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`

        """
        raise NotImplementedError

    def close(self):
        """Close underlying connection to storage backend"""
        raise NotImplementedError


class MetaTileStorageImpl(MetaTileStorageConcept):  # pragma: no cover
    """MetaTile Storage Implementation

    The default implementation of a MetaTile storage.

    :param key_concept: Instance of implementation of MetaTileKeyConcept.
    :type key_concept: :class:`~stonemason.storage.tilestorage.MetaTileKeyConcept`

    :param serializer_concept: Instance of MetaTileSerializerConcept.
    :type serializer_concept: :class:`~stonemason.storage.tilestorage.MetaTileSerializeConcept`

    :param storage_concept: Instance of PersistentStorageConcept.
    :type storage_concept: :class:`~stonemason.storage.PersistentStorageConcept`

    :param levels: The level limits of the stored MetaTile.
    :type levels: list

    :param stride: The stride of the stored MetaTile.
    :type stride: int

    :param readonly: Disable write access of the storage.
    :type readonly: bool

    """

    def __init__(self, storage, levels=range(0, 23), stride=1, readonly=False):
        assert isinstance(storage, GenericStorageConcept)

        self._levels = levels
        self._stride = stride
        self._readonly = readonly
        self._storage = storage

    @property
    def levels(self):
        """Metatile levels in the storage."""
        return self._levels

    @property
    def stride(self):
        """Stride of metatiles in the storage"""
        return self._stride

    def has(self, index):
        """Check whether given index exists in the storage."""
        assert isinstance(index, MetaTileIndex)

        return self._storage.has(index)

    def get(self, index):
        """Retrieve a `MetaTile` from the storage."""
        assert isinstance(index, MetaTileIndex)

        return self._storage.get(index)

    def put(self, metatile):
        """Store a `MetaTile` in the storage."""
        assert isinstance(metatile, MetaTile)

        if self._readonly:
            raise ReadOnlyMetaTileStorage

        if metatile.index.z not in self._levels:
            raise InvalidMetaTileIndex('Invalid MetaTile level.')
        if metatile.index.stride != self._stride:
            if metatile.index.z >> metatile.index.stride > 0:
                raise InvalidMetaTileIndex('Invalid MetaTile stride.')

        self._storage.put(metatile.index, metatile)

    def retire(self, index):
        """Delete `MetaTile` with given index."""
        assert isinstance(index, MetaTileIndex)

        if self._readonly:
            raise ReadOnlyMetaTileStorage

        self._storage.delete(index)

    def close(self):
        """Close underlying connection to storage backend."""
        self._storage.close()
