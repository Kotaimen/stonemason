# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/29/15'

import os

from .mapper import FeatureKeyConcept, SimpleFeatureKeyMode
from .serializer import FeatureSerializeConcept, RasterFeatureSerializer
from .indexer import SpatialIndexConcept, ShpSpatialIndex

from ..concept import GenericStorageImpl, PersistentStorageConcept, \
    ReadOnlyStorage

from ..backends.s3 import S3Storage
from ..backends.disk import DiskStorage


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

    def query(self, envelope, crs='EPSG:4326'):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


class FeatureStorageImpl(FeatureStorageConcept):
    def __init__(self, key_mode, serializer, storage, indexer):
        assert isinstance(key_mode, FeatureKeyConcept)
        assert isinstance(serializer, FeatureSerializeConcept)
        assert isinstance(storage, PersistentStorageConcept)
        assert isinstance(indexer, SpatialIndexConcept)

        self._storage = GenericStorageImpl(key_concept=key_mode,
                                           serializer_concept=serializer,
                                           storage_concept=storage)

        self._indexer = indexer

    @property
    def crs(self):
        return self._indexer.crs

    @property
    def envelope(self):
        return self._indexer.envelope

    def has(self, key):
        return self._storage.has(key)

    def put(self, key, feature):
        raise ReadOnlyStorage

    def get(self, key):
        return self._storage.get(key)

    def delete(self, key):
        self._storage.delete(key)

    def query(self, envelope, crs='EPSG:4326'):
        for feature_key in self._indexer.intersection(envelope, crs=crs):
            yield feature_key

    def close(self):
        self._indexer.close()
        self._storage.close()


class DiskRasterFeatureStorage(FeatureStorageImpl):
    def __init__(self, root='', index_filename='index.shp'):
        storage = DiskStorage()

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index_filename)

        FeatureStorageImpl.__init__(self,
                                    key_mode=key_mode,
                                    serializer=serializer,
                                    storage=storage,
                                    indexer=indexer)


class S3RasterFeatureStorage(FeatureStorageImpl):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False, index_filename='index.shp'):
        storage = S3Storage(access_key=access_key, secret_key=secret_key,
                            bucket=bucket, policy=policy,
                            reduced_redundancy=reduced_redundancy)

        key_mode = SimpleFeatureKeyMode()

        serializer = RasterFeatureSerializer()

        indexer = ShpSpatialIndex(storage, index_filename)

        FeatureStorageImpl.__init__(self,
                                    key_mode=key_mode,
                                    serializer=serializer,
                                    storage=storage,
                                    indexer=indexer)
