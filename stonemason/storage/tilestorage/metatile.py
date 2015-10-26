# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/25/15'

import os
import io
import six
import gzip

from stonemason.formatbundle import FormatBundle, MapWriter
from stonemason.pyramid import MetaTileIndex, MetaTile, TileCluster, \
    Hilbert, Legacy

from ..concept import StorageKeyConcept, ObjectSerializeConcept, \
    PersistentStorageConcept, GenericStorageImpl, StorageError

from ..s3 import S3Storage
from ..disk import DiskStorage


# ==============================================================================
# Exceptions for MetaTile Storage
# ==============================================================================
class MetaTileStorageError(StorageError):
    """Base MetaTile Storage Error

    The base class for all metatile storage exceptions.
    """
    pass


class ReadonlyStorage(MetaTileStorageError):
    """Read Only Storage

    Raise when trying to modify a read only storage.
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


# ==============================================================================
# MetaTile Key Mode
# ==============================================================================
class MetaTileKeyConcept(StorageKeyConcept):  # pragma: no cover
    def __init__(self, prefix='', extension='.png', sep='/', gzip=False):
        assert isinstance(prefix, six.string_types)
        assert extension.startswith('.')
        self._prefix = prefix
        self._extension = extension
        self._sep = sep

        if gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'


class HilbertKeyMode(MetaTileKeyConcept):
    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Hilbert.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class LegacyKeyMode(MetaTileKeyConcept):
    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Legacy.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class SimpleKeyMode(MetaTileKeyConcept):
    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend([str(z), str(x), str(y)])
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


KEY_MODES = dict(hilbert=HilbertKeyMode,
                 legacy=LegacyKeyMode,
                 simple=SimpleKeyMode)


def create_key_mode(mode, **kwargs):
    try:
        class_ = KEY_MODES[mode]
    except KeyError:
        raise RuntimeError('Invalid storage key mode "%s"' % mode)
    return class_(**kwargs)


# ==============================================================================
# MetaTile Serializer
# ==============================================================================
class MetaTileSerializerConcept(ObjectSerializeConcept):  # pragma: no cover
    pass


class MetaTileSerializer(MetaTileSerializerConcept):
    def __init__(self, gzip=False, mimetype='image/png'):
        self._use_gzip = bool(gzip)
        self._mimetype = mimetype

    def load(self, index, blob, metadata):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(metadata, dict)

        if self._use_gzip:
            # decompress gzip
            blob = gzip.GzipFile(fileobj=io.BytesIO(blob), mode='rb').read()

        if metadata.get('mimetype') is None:
            metadata['mimetype'] = self._mimetype

        assert set(metadata.keys()).issuperset({'mimetype', 'etag', 'mtime'})

        return MetaTile(index, data=blob, **metadata)

    def save(self, index, obj):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(obj, MetaTile)

        if obj.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        blob = obj.data

        if self._use_gzip:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode='wb') as fp:
                fp.write(blob)
            blob = buf.getvalue()

        metadata = dict(
            mimetype=obj.mimetype,
            mtime=obj.mtime,
            etag=obj.etag)

        return blob, metadata


class TileClusterSerializer(MetaTileSerializerConcept):
    def __init__(self, writer, compressed=False, mimetype='image/png'):
        assert isinstance(writer, MapWriter)
        self._compressed = compressed
        self._writer = writer
        self._mimetype = mimetype

    def load(self, index, blob, metadata):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(metadata, dict)

        metadata = metadata.copy()
        # let tilecluster figure out mimetype from cluster index,
        # since storage always assign 'application/zip' for a cluster
        if 'mimetype' in metadata:
            del metadata['mimetype']

        assert set(metadata.keys()).issuperset({'etag', 'mtime'})

        return TileCluster.from_zip(io.BytesIO(blob), metadata=metadata)

    def save(self, index, obj):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(obj, MetaTile)

        if obj.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        metadata = dict(mimetype='application/zip',
                        mtime=obj.mtime,
                        etag=obj.etag)
        cluster = TileCluster.from_metatile(obj, self._writer)
        buf = io.BytesIO()
        cluster.save_as_zip(buf, compressed=self._compressed)
        return buf.getvalue(), metadata


# ==============================================================================
# MetaTile Storage
# ==============================================================================
class MetaTileStorage(object):  # pragma: no cover
    """Persistence storage of `MetaTile`."""

    def __init__(self, key_concept, serializer, storage,
                 levels=range(0, 23), stride=1, readonly=False):
        assert isinstance(key_concept, MetaTileKeyConcept)
        assert isinstance(serializer, MetaTileSerializerConcept)
        assert isinstance(storage, PersistentStorageConcept)

        self._levels = levels
        self._stride = stride

        self._readonly = readonly

        self._storage = GenericStorageImpl(key_concept=key_concept,
                                           serializer_concept=serializer,
                                           storage_concept=storage)

    @property
    def levels(self):
        """Metatile levels in the storage."""
        return self._levels

    @property
    def stride(self):
        """Stride of metatiles in the storage"""
        return self._stride

    def has(self, index):
        """ Check whether given index exists in the storage.

        :param index: MetaTile index.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :return: Whether the metatile exists.
        :rtype: bool
        """
        assert isinstance(index, MetaTileIndex)

        return self._storage.has(index)

    def get(self, index):
        """Retrieve a `MetaTile` from the storage.

        Retrieve a `MetaTile` from the storage, returns ``None`` if its not
        found ind the storage

        :param index: MetaTile index of the MetaTile.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :returns: Retrieved tile cluster.
        :rtype: :class:`~stonemason.tilestorage.MetaTile`
        """
        assert isinstance(index, MetaTileIndex)

        return self._storage.get(index)

    def put(self, metatile):
        """Store a `MetaTile` in the storage.

        Store a `MetaTile` in the storage, overriding any existing one.

        :param metatile: MetaTile to store.
        :type metatile: :class:`~stonemason.pyramid.MetaTile`
        """
        assert isinstance(metatile, MetaTile)

        if self._readonly:
            raise ReadonlyStorage

        if metatile.index.z not in self._levels:
            raise InvalidMetaTileIndex('Invalid MetaTile level.')
        if metatile.index.stride != self._stride:
            if metatile.index.z >> metatile.index.stride > 0:
                raise InvalidMetaTileIndex('Invalid MetaTile stride.')

        self._storage.put(metatile.index, metatile)

    def retire(self, index):
        """Delete `MetaTile` with given index.

        If `MetaTile` does not present in cache, this operation has no effect.


        :param index: MetaTile index of the tile cluster.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        """
        assert isinstance(index, MetaTileIndex)

        if self._readonly:
            raise ReadonlyStorage

        self._storage.delete(index)

    def close(self):
        """Close underlying connection to storage backend"""
        self._storage.close()


class S3MetaTileStorage(MetaTileStorage):
    """ Store `MetaTile` on AWS S3.

    .. warning::
        Do *not* store AWS account access key and secret key in configuration
        files, instead, set IAM account security credentials in environment
        variables, or boto configuration file. Or an key-less authorization
        model like IAM role policy.

    .. seealso:: :mod:`boto.s3`

    :param access_key: AWS access key id, if set to `None`, try load
        from environment variable ``AWS_ACCESS_KEY_ID``, or IAM role temporary
        security credentials.
    :type access_key: str or ``None``

    :param secret_key: AWS secret key id, if set to `None`, try load
        from environment variable ``AWS_SECRET_ACCESS_KEY``, or IAM role
        temporary security credentials.
    :type secret_key: str or ``None``

    :param bucket: Required, s3 bucket name, the bucket must be created
        first with proper permissions, policy, lifecycle management,
        visioning, sever side encryption, and redundancy level.
    :type bucket: str

    :param policy: Canned policy, must be one of:

        `private`
            Owner gets full control, no one else has access rights.

        `public-read`
            Owner gets full control, no one else has read rights.

    :type policy: str

    :param reduced_redundancy: Set storage class to REDUCED_REDUNDANCY
        if set to `True`, default is `False`

    :type reduced_redundancy: bool

    :param key_mode: Specifies how the s3 key is calculated from
        metatile index, possible values are:

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        Default value is ``simple``.
    :type key_mode: str

    :param prefix: Prefix which will be prepend to generated s3 keys.
    :type prefix: str

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0-22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int


    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    """

    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False,
                 key_mode='simple', prefix='my_storage',
                 levels=range(0, 22), stride=1, format=None,
                 readonly=False):
        if not isinstance(format, FormatBundle):
            raise MetaTileStorageError('Must specify format explicitly.')

        key_mode = create_key_mode(key_mode, prefix=prefix,
                                   extension=format.tile_format.extension,
                                   sep='/')

        object_persistence = MetaTileSerializer(
            gzip=False, mimetype=format.tile_format.mimetype)

        s3storage = S3Storage(access_key=access_key, secret_key=secret_key,
                              bucket=bucket, policy=policy,
                              reduced_redundancy=reduced_redundancy)

        MetaTileStorage.__init__(self, key_mode,
                                 object_persistence,
                                 s3storage,
                                 levels=levels, stride=stride,
                                 readonly=readonly)


class DiskMetaTileStorage(MetaTileStorage):
    """ Store `MetaTile` on a file system.

    :param root: Required, root directory of the storage, must be a
        absolute filesystem path.
    :type root: str

    :param dir_mode: Specifies how the directory names are calculated from
        metatile index, possible choices are:

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        `legacy` and `hilbert` mode will limit files and subdirs under a
        directory by calculating a "hash" string from tile coordinate.
        The directory tree structure also groups adjacent geographical
        items together, improves filesystem cache performance, default
        value is ``hilbert``.
    :type dir_mode: str

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0-22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int

    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    :param gzip: Whether the metatile file stored on filesystem will be gzipped,
        default is ``False``.  Note when `gzip` is enabled, ``.gz`` is
        automatically appended to `extension`.
    :type gzip: bool
    """

    def __init__(self, root='.', dir_mode='hilbert',
                 levels=range(0, 22), stride=1,
                 format=None, readonly=False, gzip=False):
        assert isinstance(root, six.string_types)
        if not isinstance(format, FormatBundle):
            raise MetaTileStorageError('Must specify format explicitly.')
        if not os.path.isabs(root):
            raise MetaTileStorageError('Only accepts an absolute path.')

        key_mode = create_key_mode(dir_mode, prefix=root,
                                   extension=format.tile_format.extension,
                                   sep=os.sep, gzip=gzip)

        object_persistence = MetaTileSerializer(
            gzip=gzip, mimetype=format.tile_format.mimetype)

        storage = DiskStorage()

        MetaTileStorage.__init__(self, key_mode,
                                 object_persistence,
                                 storage,
                                 levels=levels, stride=stride,
                                 readonly=readonly)


class S3ClusterStorage(MetaTileStorage):
    """ Store `TileCluster` on AWS S3.

    :param access_key: AWS access key id, if set to `None`, try load
        from environment variable ``AWS_ACCESS_KEY_ID``, or IAM role temporary
        security credentials.
    :type access_key: str or ``None``

    :param secret_key: AWS secret key id, if set to `None`, try load
        from environment variable ``AWS_SECRET_ACCESS_KEY``, or IAM role
        temporary security credentials.
    :type secret_key: str or ``None``

    :param bucket: Required, s3 bucket name, the bucket must be created
        first with proper permissions, policy, lifecycle management,
        visioning, sever side encryption, and redundancy level.
    :type bucket: str

    :param policy: Canned policy, must be one of:

        `private`
            Owner gets full control, no one else has access rights, this is
            the default.

        `public-read`
            Owner gets full control, no one else has read rights.

    :type policy: str

    :param reduced_redundancy: Set storage class to REDUCED_REDUNDANCY
        if set to `True`, default is `False`

    :type reduced_redundancy: bool

    :param key_mode: Specifies how the s3 key is calculated from
        metatile index, possible values are:

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        Default value is ``simple``.

    :type key_mode: str

    :param prefix: Prefix which will be prepend to generated s3 keys.
    :type prefix: str

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0-22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int

    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    """

    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False,
                 key_mode='simple', prefix='my_storage',
                 levels=range(0, 22), stride=1, format=None,
                 readonly=False, compressed=False):
        if not isinstance(format, FormatBundle):
            raise MetaTileStorageError('Must specify format explicitly.')

        key_mode = create_key_mode(key_mode, prefix=prefix,
                                   extension='.zip',
                                   sep='/')

        object_persistence = TileClusterSerializer(
            compressed=compressed,
            writer=format.writer,
            mimetype=format.tile_format.mimetype)

        s3storage = S3Storage(access_key=access_key, secret_key=secret_key,
                              bucket=bucket, policy=policy,
                              reduced_redundancy=reduced_redundancy)

        MetaTileStorage.__init__(self, key_mode,
                                 object_persistence,
                                 s3storage,
                                 levels=levels, stride=stride,
                                 readonly=readonly)


class DiskClusterStorage(MetaTileStorage):
    """ Store `TileCluster` on a file system.

    :param root: Required, root directory of the storage, must be a
        absolute os path.
    :type root: str

    :param dir_mode: Specifies how the directory names is calculated from
        metatile index, possible values are:

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        `legacy` and `hilbert` mode will limit files and subdirs under a
        directory by calculating a "hash" string from tile coordinate.
        The directory tree structure also groups adjacent geographical
        items together, improves filesystem cache performance, default
        value is ``hilbert``.
    :type dir_mode: str

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0-22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int

    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    :param compressed: Whether to compress generated cluster zip file, file
        stored on filesystem will be gzipped, default is ``False``.
    :type compressed: bool

    """

    def __init__(self, root='.', dir_mode='hilbert',
                 levels=range(0, 22), stride=1, format=None,
                 readonly=False, compressed=False):
        assert isinstance(root, six.string_types)
        if not isinstance(format, FormatBundle):
            raise MetaTileStorageError('Must specify format explicitly.')
        if not os.path.isabs(root):
            raise MetaTileStorageError('Only accepts an absolute path.')

        key_mode = create_key_mode(dir_mode, prefix=root,
                                   extension='.zip',
                                   sep=os.sep)

        object_persistence = TileClusterSerializer(
            compressed=compressed,
            writer=format.writer,
            mimetype=format.tile_format.mimetype)

        storage = DiskStorage()

        MetaTileStorage.__init__(self, key_mode,
                                 object_persistence, storage,
                                 levels=levels, stride=stride,
                                 readonly=readonly)


# ==============================================================================
# Null MetaTile Storage
# ==============================================================================
class NullMetaTileKeyMode(MetaTileKeyConcept):
    pass


class NullMetaTileSerializer(MetaTileSerializerConcept):
    pass


class NullMetaTilePersistentStorage(PersistentStorageConcept):
    pass


class NullMetaTileStorage(MetaTileStorage):  # pragma: no cover
    """A storage stores nothing."""

    def __init__(self):
        key_mode = NullMetaTileKeyMode()
        serializer = NullMetaTileSerializer()
        storage = NullMetaTilePersistentStorage()

        MetaTileStorage.__init__(self, key_mode, serializer, storage)

    @property
    def levels(self):
        return []

    @property
    def stride(self):
        return 1

    def has(self, index):
        return False

    def get(self, index):
        return None

    def put(self, metatile):
        return

    def retire(self, index):
        return

    def close(self):
        pass


NullClusterStorage = NullMetaTileStorage

ClusterStorage = MetaTileStorage
