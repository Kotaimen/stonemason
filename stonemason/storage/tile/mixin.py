# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

import io
import six
import gzip

from stonemason.pyramid import MetaTile, MetaTileIndex

from ..concept import PersistentStorageConcept, ObjectSerializeConcept, \
    StorageKeyConcept

from .exceptions import *


class StorageMixin(object):
    """Mixin class assembles all the concepts."""

    def __init__(self, storage, serializer, key_mode,
                 levels=range(0, 23),
                 stride=1,
                 prefix=None,
                 mimetype=None, extension=None,
                 gzip=False, readonly=False):
        assert isinstance(storage, PersistentStorageConcept)
        assert isinstance(serializer, ObjectSerializeConcept)
        assert isinstance(key_mode, StorageKeyConcept)
        self._storage = storage
        self._serializer = serializer
        self._key_mode = key_mode
        self._levels = levels
        self._stride = stride
        # prefix
        assert isinstance(prefix, six.string_types)
        self._prefix = prefix

        assert extension.startswith('.')
        self._extension = extension
        self._mimetype = mimetype

        # readonly flag
        self._readonly = bool(readonly)

        # gzipped flag
        self._use_gzip = bool(gzip)
        if self._use_gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'

    @property
    def levels(self):
        return self._levels

    @property
    def stride(self):
        return self._stride

    def get(self, index):
        assert isinstance(index, MetaTileIndex)
        storage_key = self._key_mode(self._prefix, index, self._extension)

        blob, metadata = self._storage.retrieve(storage_key)
        if blob is None:
            return None
        # verify metadata structure
        assert set(metadata.keys()) == {'mimetype', 'etag', 'mtime'}
        # if storage failed to preserve mimetype, use default value
        if metadata['mimetype'] is None:
            metadata['mimetype'] = self._mimetype

        if self._use_gzip:
            # decompress gzip
            blob = gzip.GzipFile(fileobj=io.BytesIO(blob), mode='rb').read()

        return self._serializer.load(index, blob, metadata)

    def has(self, index):
        storage_key = self._key_mode(self._prefix, index, self._extension)
        return self._storage.exists(storage_key)

    def put(self, metatile):
        if self._readonly:
            raise ReadonlyStorage
        assert isinstance(metatile, MetaTile)
        if metatile.index.z not in self._levels:
            raise InvalidMetaTileIndex('Invalid MetaTile level.')
        if metatile.index.stride != self._stride:
            if metatile.index.z >> metatile.index.stride > 0:
                raise InvalidMetaTileIndex('Invalid MetaTile stride.')
        if metatile.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        storage_key = self._key_mode(self._prefix, metatile.index,
                                     self._extension)

        blob, metadata = self._serializer.save(metatile)

        if self._use_gzip:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as fp:
                fp.write(blob)
            blob = buf.getvalue()

        self._storage.store(storage_key, blob, metadata)

    def retire(self, index):
        if self._readonly:
            raise ReadonlyStorage

        storage_key = self._key_mode(self._prefix, index, self._extension)

        self._storage.delete(storage_key)

    def close(self):
        self._storage.close()
