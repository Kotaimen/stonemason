# -*- encoding: utf-8 -*-

"""
    stonemason.tilestorage.s3
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    S3 based storages.

"""

__author__ = 'kotaimen'
__date__ = '1/29/15'

import email
import time

import boto
import boto.s3
from boto.s3.key import Key
import six

from stonemason.formatbundle import FormatBundle
from .tilestorage import ClusterStorage, MetaTileStorage, \
    PersistenceStorageConcept, create_key_mode, MetaTileSerializer, \
    TileClusterSerializer, StorageMixin
from .exceptions import TileStorageError


def s3timestamp2mtime(timestamp):
    """Convert RFC 2822 datetime string used by s3 to mtime."""
    modified = email.utils.parsedate_tz(timestamp)
    if modified is None:
        return None
    mtime = email.utils.mktime_tz(modified)
    return float(mtime)


def mtime2s3timestamp(mtime):
    """Convert mtime to RFC 2822 datetime string."""
    return email.utils.formatdate(time.time())


class S3Storage(PersistenceStorageConcept):
    """Use AWS Simple Storage Service as persistence backend."""

    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False):
        self._conn = boto.connect_s3(aws_access_key_id=access_key,
                                     aws_secret_access_key=secret_key, )
        self._bucket = self._conn.get_bucket(bucket_name=bucket)

        assert policy in ['private', 'public-read']
        self._policy = policy
        self._reduced_redundancy = reduced_redundancy

    def exists(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        return s3key.exists()

    def retrieve(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        if not s3key.exists():
            # Check key existence first otherwise get_content() will
            # retry several times, which slows thing down a lot.
            return None, None
        blob = s3key.get_contents_as_string()
        if six.PY2:
            etag = s3key.md5
        else:
            # Key.md5 returns bytes on py3 despite it is actually a hex string
            etag = s3key.md5.decode()
        metadata = dict(etag=etag,
                        mimetype=s3key.content_type,
                        mtime=s3timestamp2mtime(s3key.last_modified))

        return blob, metadata

    def store(self, key, blob, metadata):
        assert isinstance(key, six.string_types)
        assert isinstance(blob, bytes)
        assert isinstance(metadata, dict)
        assert 'mimetype' in metadata
        assert 'etag' in metadata
        assert 'mtime' in metadata

        s3key = Key(bucket=self._bucket, name=key)
        s3key.content_type = metadata['mimetype']
        s3key.md5 = metadata['etag']
        s3key.last_modified = mtime2s3timestamp(metadata['mtime'])
        s3key.set_contents_from_string(blob,
                                       replace=True,
                                       policy=self._policy,
                                       reduced_redundancy=self._reduced_redundancy)

    def delete(self, key):
        s3key = Key(bucket=self._bucket, name=key)
        s3key.delete()

    def close(self):
        self._conn.close()


class S3MetaTileStorage(StorageMixin, MetaTileStorage):
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
    :type dir_mode: str

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
            raise TileStorageError('Must specify format explicitly.')

        s3storage = S3Storage(access_key=access_key, secret_key=secret_key,
                              bucket=bucket, policy=policy,
                              reduced_redundancy=reduced_redundancy)

        key_mode = create_key_mode(key_mode, sep='/')

        object_persistence = MetaTileSerializer()

        StorageMixin.__init__(self, s3storage, object_persistence, key_mode,
                              levels=levels, stride=stride, prefix=prefix,
                              mimetype=format.tile_format.mimetype,
                              extension=format.tile_format.extension,
                              gzip=False, readonly=readonly)


class S3ClusterStorage(StorageMixin, ClusterStorage):
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

    :type dir_mode: str

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

    :param splitter: A :class:`~stonemason.tilestorage.Splitter` instance
        to split `MetaTile` data into `Tile` data.
    :type splitter: :class:`~stonemason.tilestorage.Splitter`
    """

    def __init__(self, access_key=None, secret_key=None,
                 bucket='my_bucket', policy='private',
                 reduced_redundancy=False,
                 key_mode='simple', prefix='my_storage',
                 levels=range(0, 22), stride=1, format=None,
                 readonly=False, compressed=False):
        if not isinstance(format, FormatBundle):
            raise TileStorageError('Must specify format explicitly.')

        s3storage = S3Storage(access_key=access_key, secret_key=secret_key,
                              bucket=bucket, policy=policy,
                              reduced_redundancy=reduced_redundancy)

        key_mode = create_key_mode(key_mode, sep='/')

        object_persistence = TileClusterSerializer(compressed=compressed,
                                                   writer=format.writer)

        StorageMixin.__init__(self, s3storage, object_persistence, key_mode,
                              levels=levels, stride=stride, prefix=prefix,
                              mimetype=format.tile_format.mimetype,
                              extension='.zip',
                              gzip=False, readonly=readonly)
