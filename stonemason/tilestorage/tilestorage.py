# -*- encoding: utf-8 -*-

"""
    stonemason.tilestorage.tilestorage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Persistence storage of tiles.
"""

__author__ = 'kotaimen'
__date__ = '1/18/15'

import io
import gzip

import six

from stonemason.pyramid import MetaTileIndex, MetaTile, Hilbert, Legacy
from stonemason.formatbundle import MapWriter
from .cluster import TileCluster
from .exceptions import *


#
# Public IF
#

class ClusterStorage(object):  # pragma: no cover
    """Homologous persistence storage of `TileCluster`.

    Homologous means single storage can only store single type of TileClusters.
    All MetaTiles put into the storage must have same `mimetype`, `stride` and
    `buffering`.
    """

    @property
    def levels(self):
        """Cluster levels in the storage."""
        raise NotImplementedError

    @property
    def stride(self):
        """Stride of clusters in the storage"""
        raise NotImplementedError

    def get(self, index):
        """Retrieve a `TileCluster` from the storage.

        Retrieve a `TileCluster` from the storage, returns ``None`` if its not
        found ind the storage

        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :returns: Retrieved TileCluster.
        :rtype: :class:`~stonemason.tilestorage.TileCluster` or ``None``
        """
        raise NotImplementedError

    def has(self, index):
        """ Check whether given index exists in the storage.

        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :return: Whether the cluster exists.
        :rtype: bool
        """
        raise NotImplementedError

    def put(self, metatile):
        """Store a `MetaTile` in the storage as `TileCluster`.

        Store a `MetaTile` in the storage as `TileCluster`, overriding
        any existing one.

        :param metatile: MetaTile to store.
        :type metatile: :class:`~stonemason.pyramid.MetaTile`
        """

        raise NotImplementedError

    def retire(self, index):
        """Delete `TileCluster` with given index.

        If `TileCluster` does not present in cache, this operation has no effect.


        :param index: MetaTile index of the TileCluster.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        """
        raise NotImplementedError

    def close(self):
        """Close underlying connection to storage backend"""
        raise NotImplementedError


class MetaTileStorage(object):  # pragma: no cover
    """Persistence storage of `MetaTile`."""


    @property
    def levels(self):
        """Metatile levels in the storage."""
        raise NotImplementedError

    @property
    def stride(self):
        """Stride of metatiles in the storage"""
        raise NotImplementedError

    def get(self, index):
        """Retrieve a `MetaTile` from the storage.

        Retrieve a `MetaTile` from the storage, returns ``None`` if its not
        found ind the storage

        :param index: MetaTile index of the MetaTile.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :returns: Retrieved tile cluster.
        :rtype: :class:`~stonemason.tilestorage.MetaTile`
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

    def put(self, metatile):
        """Store a `MetaTile` in the storage.

        Store a `MetaTile` in the storage, overriding any existing one.

        :param metatile: MetaTile to store.
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


#
# Internal IF
#

class PersistenceStorageConcept(object):  # pragma: no cover
    """Represents an actual storage implement."""

    def exists(self, key):
        """Check whether given key exists in the storage"""
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
        """Close underlying connection to storage backend"""
        raise NotImplementedError


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


class HilbertKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend(Hilbert.coord2dir(index.z, index.x, index.y))
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


class LegacyKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend(Legacy.coord2dir(index.z, index.x, index.y))
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


class SimpleKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend([str(index.z), str(index.x), str(index.y)])
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


KEY_MODES = dict(hilbert=HilbertKeyMode,
                 legacy=LegacyKeyMode,
                 simple=SimpleKeyMode, )


def create_key_mode(mode, sep):
    assert isinstance(sep, six.string_types)
    try:
        class_ = KEY_MODES[mode]
    except KeyError:
        raise RuntimeError('Invalid storage key mode "%s"' % mode)
    return class_(sep=sep)


class ObjectSerializeConcept(object):  # pragma: no cover
    """Represents how a object (`MetaTile`/`TileCluster` as of now) is
    persisted as binary data."""

    def load(self, index, blob, metadata):
        raise NotImplementedError

    def save(self, metatile):
        raise NotImplementedError


class MetaTileSerializer(ObjectSerializeConcept):
    def load(self, index, blob, metadata):
        return MetaTile(index, data=blob, **metadata)

    def save(self, metatile):
        metadata = dict(mimetype=metatile.mimetype,
                        mtime=metatile.mtime,
                        etag=metatile.etag)
        return metatile.data, metadata


class TileClusterSerializer(ObjectSerializeConcept):
    def __init__(self, writer, compressed=False):
        assert isinstance(writer, MapWriter)
        self._compressed = compressed
        self._writer = writer

    def load(self, index, blob, metadata):
        metadata = metadata.copy()
        # let tilecluster figure out mimetype from cluster index,
        # since storage always assign 'application/zip' for a cluster
        del metadata['mimetype']
        return TileCluster.from_zip(io.BytesIO(blob), metadata=metadata)

    def save(self, metatile):
        metadata = dict(mimetype='application/zip',
                        mtime=metatile.mtime,
                        etag=metatile.etag)
        cluster = TileCluster.from_metatile(metatile, self._writer)
        buf = io.BytesIO()
        cluster.save_as_zip(buf, compressed=self._compressed)
        return buf.getvalue(), metadata


class StorageMixin(object):
    """Mixin class assembles all the concepts."""

    def __init__(self, storage, serializer, key_mode,
                 levels=range(0, 23),
                 stride=1,
                 prefix=None,
                 mimetype=None, extension=None,
                 gzip=False, readonly=False):
        assert isinstance(storage, PersistenceStorageConcept)
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


#
# "Null" storage
#
class NullClusterStorage(ClusterStorage):  # pragma: no cover
    """A storage stores nothing."""

    @property
    def levels(self):
        return []

    @property
    def stride(self):
        return 1

    def get(self, index):
        return None

    def put(self, metatile):
        return

    def retire(self, index):
        return


class NullMetaTileStorage(MetaTileStorage):  # pragma: no cover
    """A storage stores nothing."""

    @property
    def levels(self):
        return []

    @property
    def stride(self):
        return 1

    def get(self, index):
        return None

    def put(self, metatile):
        return

    def retire(self, index):
        return

