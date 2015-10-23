# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

class StorageKeyConcept(object):  # pragma: no cover
    """Controls how a meta tile index is converted to key in the storage."""

    def __init__(self, sep='/'):
        """:param sep: Separator used to join path fragments."""
        self._sep = sep

    def __call__(self, prefix, index, extension):
        """
        :param prefix: Prefix of the pathname.
        :param index: Metatile index.
        :param extension: Extension of the basename.
        :return: Calculated pathname.
        :rtype: str
        """
        pass


class ObjectSerializeConcept(object):  # pragma: no cover
    """Represents how a object (`MetaTile`/`TileCluster` as of now) is
    persisted as binary data."""

    def load(self, index, blob, metadata):
        raise NotImplementedError

    def save(self, metatile):
        raise NotImplementedError


class PersistentStorageConcept(object):  # pragma: no cover
    """Represents an actual storage implement."""

    def exists(self, key):
        """Check whether given key exists in the storage."""
        raise NotImplementedError

    def retrieve(self, key):
        """Retrieve ``(blob, metadata)`` of given pathname from storage."""
        raise NotImplementedError

    def store(self, key, blob, metadata):
        """Store given `blob` and `metadata` to storage using `pathname`."""
        raise NotImplementedError

    def delete(self, key):
        """Delete object with given `pathname`."""
        raise NotImplementedError

    def close(self):
        """Close underlying connection to storage backend."""
        raise NotImplementedError
