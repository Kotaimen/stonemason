# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/29/15'

from ..concept import StorageKeyConcept, ObjectSerializeConcept, \
    PersistentStorageConcept, GenericStorageImpl, ReadOnlyStorage


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
        """A literal string that represents the coordinate reference system of
        the storage.
        """
        raise NotImplementedError

    @property
    def envelope(self):
        """A tuple of ``(minx, miny, maxx, maxy)`` that represents the bounding
        box of the storage.
        """
        raise NotImplementedError

    def index(self, key, feature):
        """Add a new feature into the index.

        :param key: A literal string that identified the feature.
        :type key: str

        :param feature: A feature object.
        :type feature: Object
        """
        raise NotImplementedError

    def intersection(self, envelope, crs='EPSG:4326'):
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

    @property
    def envelope(self):
        raise NotImplementedError

    def has(self, key):
        raise NotImplementedError

    def put(self, key, feature):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def intersection(self, envelope, crs='EPSG:4326', size=None):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class FeatureStorageImpl(FeatureStorageConcept):
    def __init__(self, key_mode, serializer, storage):
        assert isinstance(key_mode, FeatureKeyConcept)
        assert isinstance(serializer, FeatureSerializeConcept)
        assert isinstance(storage, PersistentStorageConcept)

        self._storage = GenericStorageImpl(key_concept=key_mode,
                                           serializer_concept=serializer,
                                           storage_concept=storage)

    def has(self, key):
        return self._storage.has(key)

    def put(self, key, feature):
        raise ReadOnlyStorage
        # self._storage.put(key, feature)
        # self._indexer.index(key, feature)

    def get(self, key):
        return self._storage.get(key)

    def delete(self, key):
        self._storage.delete(key)

    def close(self):
        self._storage.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
