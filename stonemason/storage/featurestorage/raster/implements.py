# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/4/15'

import os
from stonemason.storage.backends.s3 import S3Storage, S3HttpStorage
from stonemason.storage.backends.disk import DiskStorage
from stonemason.storage.concept import GenericStorageImpl, ReadOnlyStorage
from stonemason.storage.featurestorage.concept import FeatureStorageImpl
from .mapper import SimpleFeatureKeyMode
from .serializer import RasterFeatureSerializer
from .indexer import ShpSpatialIndex


class RasterStorageConcept(FeatureStorageImpl):
    def put(self, key, feature):
        """Do not allow write access for now."""
        raise ReadOnlyStorage

    def delete(self, key):
        """Do not allow write access for now."""
        raise ReadOnlyStorage


class DiskRasterStorage(RasterStorageConcept):
    def __init__(self, prefix='', indexname='index.shp'):
        sep = os.sep

        key_mode = SimpleFeatureKeyMode(prefix=prefix, sep=sep)
        serializer = RasterFeatureSerializer()
        persistent = DiskStorage()

        storage = GenericStorageImpl(key_concept=key_mode,
                                     serializer_concept=serializer,
                                     storage_concept=persistent)

        indexer = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        RasterStorageConcept.__init__(self, storage=storage, index=indexer)


class S3RasterStorage(RasterStorageConcept):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', prefix='', policy='private',
                 reduced_redundancy='STANDARD', indexname='index.shp'):
        sep = '/'

        key_mode = SimpleFeatureKeyMode(prefix=prefix, sep=sep)
        serializer = RasterFeatureSerializer()
        persistent = S3Storage(access_key=access_key, secret_key=secret_key,
                               bucket=bucket, policy=policy,
                               reduced_redundancy=reduced_redundancy)

        storage = GenericStorageImpl(key_concept=key_mode,
                                     serializer_concept=serializer,
                                     storage_concept=persistent)

        indexer = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        RasterStorageConcept.__init__(self, storage=storage, index=indexer)


class S3HttpRasterStorage(RasterStorageConcept):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', prefix='', policy='private',
                 reduced_redundancy='STANDARD', indexname='index.shp'):
        sep = '/'

        key_mode = SimpleFeatureKeyMode(prefix=prefix, sep=sep)
        serializer = RasterFeatureSerializer()
        persistent = S3HttpStorage(access_key=access_key, secret_key=secret_key,
                               bucket=bucket, policy=policy,
                               reduced_redundancy=reduced_redundancy)

        storage = GenericStorageImpl(key_concept=key_mode,
                                     serializer_concept=serializer,
                                     storage_concept=persistent)

        indexer = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        RasterStorageConcept.__init__(self, storage=storage, index=indexer)
