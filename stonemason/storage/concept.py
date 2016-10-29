# -*- encoding: utf-8 -*-
"""
    stonemason.storage.concept
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Basic concept and interface of stonemason storage.
"""
__author__ = 'ray'
__date__ = '10/22/15'

import logging


# ==============================================================================
# Basic Exceptions for All Storage
# ==============================================================================
class StorageError(Exception):
    """Basic Storage Error

    The base class for all storage exceptions.
    """
    pass


class StorageKeyError(StorageError):
    """Storage Key Error

    The base class for all exceptions when mapping index objects to storage
    keys.
    """
    pass


class ObjectSerializeError(StorageError):
    """Object Serialize Error

    The base class for all serialization exceptions.
    """
    pass


class ObjectLoadError(ObjectSerializeError):
    """Object Loading Error

    The base class for all exceptions when loading objects from binary blob.
    """
    pass


class ObjectSaveError(ObjectSerializeError):
    """Object Saving Error

    The base class for all exceptions when saving objects to binary blob.
    """
    pass


class PersistentStorageError(StorageError):
    """Persistent Storage Error

    The base class for all internal storage exceptions.
    """
    pass


class ReadOnlyStorageError(StorageError):
    pass

# ==============================================================================
# Storage Concepts
# ==============================================================================
class StorageKeyConcept(object):  # pragma: no cover
    """Storage Key Interface

    Controls how a index object is converted to a key string in the storage.
    """

    def __call__(self, index):
        """Make a key string from index object.

        :param index: Storage index object.
        :type index: object

        :return: A valid storage key.
        :rtype: str

        """

        pass


class ObjectSerializeConcept(object):  # pragma: no cover
    """Object Serializer Interface

    Represents how a object is persisted as binary data.
    """

    def load(self, index, blob, metadata):
        """Load object from binary blob and metadata

        :param index: Storage index object.
        :type index: object

        :param blob: Binary data.
        :type blob: str

        :param metadata: Optional info of the data.
        :type metadata: dict

        :return: A stored object.
        :rtype: object

        """
        raise NotImplementedError

    def save(self, index, obj):
        """Dump object to binary with its metadata.

        :param index: Storage index object.
        :type index: object

        :param obj: Object to dump.
        :type obj: object

        :return: A tuple of binary data and its metadata dict.
        :rtype: (str, dict)

        """
        raise NotImplementedError


class PersistentStorageConcept(object):  # pragma: no cover
    """Persistent Storage Interface

    Represents an actual storage interface.
    """

    def exists(self, key):
        """Check whether given key exists in the storage.

        :param key: A literal string that identifies the object.
        :type key: str

        :return: True if key exists.
        :rtype: bool

        """
        raise NotImplementedError

    def retrieve(self, key):
        """Retrieve ``(blob, metadata)`` of given pathname from storage.

        :param key: A literal string that identifies the object.
        :type key: str

        :return: A tuple of binary data and its metadata dict.
        :rtype: (str, dict)

        """
        raise NotImplementedError

    def store(self, key, blob, metadata):
        """Store given `blob` and `metadata` to storage using `pathname`.

        :param key: A literal string that identifies the object.
        :type key: str

        :param blob: Binary data.
        :type blob: str

        :param metadata: Optional info of the data.
        :type metadata: dict

        """
        raise NotImplementedError

    def retire(self, key):
        """Delete object with given `pathname`.

        :param key: A literal string that identifies the object.
        :type key: str

        """
        raise NotImplementedError

    def close(self):
        """Close underlying connection to storage backend."""
        raise NotImplementedError


class SpatialIndexConcept(object):

    def intersection(self, envelope):
        raise NotImplementedError


# ==============================================================================
# Geographic Storage
# ==============================================================================
class GeographicStorageConcept(object):

    def index(self):
        raise NotImplementedError

    def has(self, index):
        """Check whether given index exists.

        :param index: Storage index object.
        :type index: object

        """
        raise NotImplementedError

    def put(self, index, obj):
        """Store a given object into the storage with a given index.

        :param index: Storage index object.
        :type index: object

        :param obj: Object to store.
        :type obj: object

        """
        raise NotImplementedError

    def get(self, index):
        """Get the object with a given index.

        :param index: Storage index object.
        :type index: object

        """
        raise NotImplementedError

    def delete(self, index):
        """Delete the object with a given index.

        :param index: Storage index object.
        :type index: object

        """
        raise NotImplementedError

    def close(self):
        """Close the storage"""
        raise NotImplementedError


class GeographicStorageImpl(GeographicStorageConcept):
    """Generic Storage Implementation

    A generic storage implemented by composing various implement of key,
    serializer and storage concepts.

    :param key_concept: Instance of implementation of StorageKeyConcept.
    :type key_concept: :class:`~stonemason.storage.StorageKeyConcept`

    :param serializer_concept: Instance of implementation of ObjectSerializeConcept.
    :type serializer_concept: :class:`~stonemason.storage.ObjectSerializeConcept`

    :param storage_concept: Instance of implementation of PersistentStorageConcept.
    :type storage_concept: :class:`~stonemason.storage.PersistentStorageConcept`

    """

    def __init__(self, keymodel, serializer, backend, spatialindex=None):
        assert isinstance(keymodel, StorageKeyConcept)
        assert isinstance(serializer, ObjectSerializeConcept)
        assert isinstance(backend, PersistentStorageConcept)
        if spatialindex:
            assert isinstance(spatialindex, SpatialIndexConcept)


        self._keymode = keymodel
        self._serializer = serializer
        self._spatialindex = spatialindex
        self._backend = backend

        self._logger = logging.getLogger(__name__)

    @property
    def index(self):
        return self._spatialindex

    def has(self, index):
        """Check whether given index exists."""
        self._logger.debug('Has object with index %s.' % repr(index))
        storage_key = self._keymode(index)
        return self._backend.exists(storage_key)

    def put(self, index, obj):
        """Store a given object into the storage with a given index."""
        self._logger.debug('Put object with index %s.' % repr(index))

        storage_key = self._keymode(index)
        blob, metadata = self._serializer.save(index, obj)

        self._backend.store(storage_key, blob, metadata)

    def get(self, index):
        """Get the object with a given index."""
        self._logger.debug('Get object with index %s.' % repr(index))

        storage_key = self._keymode(index)

        blob, metadata = self._backend.retrieve(storage_key)
        if blob is None:
            return None

        obj = self._serializer.load(index, blob, metadata)

        return obj

    def delete(self, index):
        """Delete the object with a given index."""
        self._logger.debug('Delete object with index %s.' % repr(index))

        storage_key = self._keymode(index)
        self._backend.retire(storage_key)

    def close(self):
        """Close the storage"""
        self._logger.debug('Closing storage.')
        self._backend.close()


class NullStorage(GeographicStorageConcept):
    """Null Storage

    A dummy storage that stores nothing.
    """
    def index(self):
        raise None

    def has(self, index):
        return False

    def put(self, index, obj):
        return

    def get(self, index):
        return None

    def delete(self, index):
        return

    def close(self):
        return
