# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/25/15'

import os

import six

from stonemason.formatbundle import FormatBundle
from stonemason.pyramid import MetaTileIndex, MetaTile

from ..concept import PersistentStorageConcept, GenericStorageImpl

from ..backends.s3 import S3Storage
from ..backends.disk import DiskStorage

from .errors import InvalidMetaTileIndex, ReadonlyStorage, MetaTileStorageError
from .mapper import MetaTileKeyConcept, create_key_mode
from .serializer import MetaTileSerializerConcept, MetaTileSerializer, \
    TileClusterSerializer


# ==============================================================================
# MetaTile Storage
# ==============================================================================
class MetaTileStorageConcept(object):
    @property
    def levels(self):
        """Metatile levels in the storage."""
        raise NotImplementedError

    @property
    def stride(self):
        """Stride of metatiles in the storage"""
        raise NotImplementedError

    def has(self, index):
        """ Check whether given index exists in the storage.

        :param index: MetaTile index.
        :type index: :class:`~stonemason.tilestorage.MetaTileIndex`
        :return: Whether the metatile exists.
        :rtype: bool
        """
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


class MetaTileStorageImpl(MetaTileStorageConcept):  # pragma: no cover
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


class S3MetaTileStorage(MetaTileStorageImpl):
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

        MetaTileStorageImpl.__init__(self, key_mode,
                                     object_persistence,
                                     s3storage,
                                     levels=levels, stride=stride,
                                     readonly=readonly)


class DiskMetaTileStorage(MetaTileStorageImpl):
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

        MetaTileStorageImpl.__init__(self, key_mode,
                                     object_persistence,
                                     storage,
                                     levels=levels, stride=stride,
                                     readonly=readonly)


class S3ClusterStorage(MetaTileStorageImpl):
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

        MetaTileStorageImpl.__init__(self, key_mode,
                                     object_persistence,
                                     s3storage,
                                     levels=levels, stride=stride,
                                     readonly=readonly)


class DiskClusterStorage(MetaTileStorageImpl):
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

        MetaTileStorageImpl.__init__(self, key_mode,
                                     object_persistence, storage,
                                     levels=levels, stride=stride,
                                     readonly=readonly)


# ==============================================================================
# Null MetaTile Storage
# ==============================================================================
class NullMetaTileStorage(MetaTileStorageConcept):  # pragma: no cover
    """A storage stores nothing."""

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


# XXX: for backward compatible
ClusterStorage = MetaTileStorageConcept
NullClusterStorage = NullMetaTileStorage
