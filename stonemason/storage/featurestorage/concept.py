# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/29/15'

from ..concept import GenericStorageConcept, StorageKeyConcept, \
    ObjectSerializeConcept, StorageError


class FeatureStorageError(StorageError):
    pass


class InvalidFeatureIndex(FeatureStorageError):
    pass


class ReadOnlyFeatureStorage(FeatureStorageError):
    """Read Only Storage

    Raise when storage is read only.
    """
    pass


class FeatureKeyConcept(StorageKeyConcept):  # pragma: no cover
    """Feature Key Concept

    The ``FeatureKeyConcept`` maps Geographic id of feature to a literal key
    string.
    """
    pass


class FeatureSerializeConcept(ObjectSerializeConcept):  # pragma: no cover
    """Feature Serializer Concept

    The ``FeatureSerializeConcept`` converts between a geographic feature and
    binary blob.
    """
    pass


class SpatialIndexConcept(object):  # pragma: no cover
    """Spatial Index Concept

    The ``SpatialIndexConcept`` supports geographic query on indexed features.
    """

    @property
    def crs(self):
        raise NotImplementedError

    def insert(self, key, feature):
        """Insert a new feature into the index.

        :param key: A literal string that identified the feature.
        :type key: str

        :param feature: A feature object.
        :type feature: Object
        """
        raise NotImplementedError

    def erase(self, key):
        """Erase a feature from the index.

        :param key: A literal string that identified the feature.
        :type key: str
        """
        raise NotImplementedError

    def intersection(self, envelope):
        """Return reference of features in the shared area

        :param envelope: A tuple of ``(minx, miny, maxx, maxy)`` that represents
            querying bounding box.
        :type envelope: tuple

        :param crs: A literal string that represents the querying projection.
        :type crs: str
        """
        raise NotImplementedError

    def close(self):
        """Clean up"""
        raise NotImplementedError


class FeatureStorageConcept(object):  # pragma: no cover
    @property
    def crs(self):
        raise NotImplementedError

    def has(self, key):
        raise NotImplementedError

    def put(self, key, feature):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def intersection(self, envelope):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class FeatureStorageImpl(FeatureStorageConcept):
    def __init__(self, storage, index):
        assert isinstance(storage, GenericStorageConcept)
        assert isinstance(index, SpatialIndexConcept)

        self._storage = storage
        self._indexer = index

    @property
    def crs(self):
        return self._indexer.crs

    def has(self, key):
        return self._storage.has(key)

    def put(self, key, feature):
        self._storage.put(key, feature)

    def get(self, key):
        return self._storage.get(key)

    def delete(self, key):
        self._storage.delete(key)

    def intersection(self, envelope):
        return list(key for key in self._indexer.intersection(envelope))

    def close(self):
        self._storage.close()
