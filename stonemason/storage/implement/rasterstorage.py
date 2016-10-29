# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/28/16'

import os
from stonemason.storage.backends.s3 import S3Storage, S3HttpStorage
from stonemason.storage.backends.disk import DiskStorage
from stonemason.storage.concept import GeographicStorageImpl, ReadOnlyStorageError
from stonemason.storage.keymodel import PrefixKeyMode
from stonemason.storage.serializer import RasterSerializer
from stonemason.storage.spatialindex import ShpSpatialIndex


class DiskRasterStorage(GeographicStorageImpl):
    def __init__(self, prefix='', indexname='index.shp'):
        sep = os.sep

        key_mode = PrefixKeyMode(prefix=prefix, sep=sep)
        serializer = RasterSerializer()
        persistent = DiskStorage()
        spatialindex = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        GeographicStorageImpl.__init__(self, keymodel=key_mode,
                                       serializer=serializer,
                                       backend=persistent,
                                       spatialindex=spatialindex)

    def put(self, index, obj):
        raise ReadOnlyStorageError

    def delete(self, index):
        raise ReadOnlyStorageError


class S3RasterStorage(GeographicStorageImpl):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', prefix='', policy='private',
                 reduced_redundancy='STANDARD', indexname='index.shp'):
        sep = '/'

        key_mode = PrefixKeyMode(prefix=prefix, sep=sep)
        serializer = RasterSerializer()
        persistent = S3Storage(
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket, policy=policy,
            reduced_redundancy=reduced_redundancy)

        spatialindex = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        GeographicStorageImpl.__init__(self, keymodel=key_mode,
                                       serializer=serializer,
                                       backend=persistent,
                                       spatialindex=spatialindex)

    def put(self, index, obj):
        raise ReadOnlyStorageError

    def delete(self, index):
        raise ReadOnlyStorageError


class S3HttpRasterStorage(GeographicStorageImpl):
    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', prefix='', policy='private',
                 reduced_redundancy='STANDARD', indexname='index.shp'):
        sep = '/'

        key_mode = PrefixKeyMode(prefix=prefix, sep=sep)
        serializer = RasterSerializer()
        persistent = S3HttpStorage(
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket, policy=policy,
            reduced_redundancy=reduced_redundancy)

        spatialindex = ShpSpatialIndex.from_persistent_storage(
            persistent, index_key=sep.join([prefix, indexname]))

        GeographicStorageImpl.__init__(self, keymodel=key_mode,
                                       serializer=serializer,
                                       backend=persistent,
                                       spatialindex=spatialindex)

    def put(self, index, obj):
        raise ReadOnlyStorageError

    def delete(self, index):
        raise ReadOnlyStorageError
