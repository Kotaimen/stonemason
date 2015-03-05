# -*- encoding: utf-8 -*-

"""
    stonemason.provider.tilestorage.disk
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Disk based storages.

"""
__author__ = 'kotaimen'
__date__ = '1/23/15'

import os
import errno
import sys

import six

from stonemason.util.tempfn import generate_temp_filename
from stonemason.provider.formatbundle import FormatBundle

from .tilestorage import ClusterStorage, MetaTileStorage, \
    PersistenceStorageConcept, create_key_mode, MetaTileSerializer, \
    TileClusterSerializer, StorageMixin

from .exceptions import TileStorageError


def safe_makedirs(name):
    try:
        # exist_ok option only available on python3
        os.makedirs(name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # Ignore "already exists" error because os.makedirs
            # does not check dir exists at each creation step
            pass
        else:
            raise


class DiskStorage(PersistenceStorageConcept):
    """Use regular filesystem as persistence backend."""

    def __init__(self):
        pass

    def retrieve(self, key):
        pathname = key
        if not os.path.exists(pathname):
            # not exist
            return None, None

        with open(pathname, 'rb') as fp:
            blob = fp.read()
        mtime = os.stat(pathname).st_mtime

        return blob, dict(mimetype=None, mtime=mtime, etag=None)

    def store(self, key, blob, metadata):
        assert isinstance(key, six.string_types)
        assert isinstance(blob, bytes)
        assert isinstance(metadata, dict)
        assert 'mtime' in metadata

        pathname = key

        dirname, basename = os.path.split(pathname)

        # create directory first
        if not (os.path.exists(pathname) and os.path.isdir(pathname)):
            safe_makedirs(dirname)

        # generate temp file name
        tempname = generate_temp_filename(dirname, prefix=basename)

        with open(tempname, 'wb') as fp:
            fp.write(blob)

        # set file time to tile timestamp
        mtime = metadata['mtime']
        if mtime:
            os.utime(tempname, (mtime, mtime))

        # move it into place
        if sys.platform == 'win32':
            if os.path.exists(pathname):
                # os.rename is not atomic on windows
                os.remove(pathname)

        os.rename(tempname, pathname)

    def delete(self, key):
        pathname = key
        try:
            os.unlink(pathname)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # file not found, ignore
                pass
            else:
                raise

    def close(self):
        pass


class DiskMetaTileStorage(StorageMixin, MetaTileStorage):
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

    :param pyramid: The :class:`~stonemason.provider.pyramid.Pyramid` of the
        storage describes tile pyramid model.
    :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`

    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.provider.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    :param gzip: Whether the metatile file stored on filesystem will be gzipped,
        default is ``False``.  Note when `gzip` is enabled, ``.gz`` is
        automatically appended to `extension`.
    :type gzip: bool
    """

    def __init__(self, root='.', dir_mode='hilbert', pyramid=None,
                 format=None, readonly=False, gzip=False):
        assert isinstance(root, six.string_types)
        if not isinstance(format, FormatBundle):
            raise TileStorageError('Must specify format explicitly.')
        if not os.path.isabs(root):
            raise TileStorageError('Only accepts an absolute path.')

        storage = DiskStorage()

        key_mode = create_key_mode(dir_mode, sep=os.sep)

        object_persistence = MetaTileSerializer()

        StorageMixin.__init__(self, storage, object_persistence, key_mode,
                              pyramid=pyramid, prefix=root,
                              mimetype=format.tile_format.mimetype,
                              extension=format.tile_format.extension,
                              gzip=gzip, readonly=readonly)


class DiskClusterStorage(StorageMixin, ClusterStorage):
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

    :param pyramid: The :class:`~stonemason.provider.pyramid.Pyramid` of the
        storage describes tile pyramid model.
    :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`

    :param format: `FormatBundle` of the storage which specifies:

        - `mimetype` of the tiles stored in the storage,
        - `exension` of the tiles, Note if `gzip` option is set to ``True``,
          ``.gz`` is appended to extension.
        - How to split a `MetaTile` into tiles.

    :type format: :class:`~stonemason.provider.formatbundle.FormatBundle`

    :param readonly: Whether the storage is created in read only mode, default
        is ``False``, :meth:`put` and :meth:`retire` always raises
        :exc:`ReadOnlyStorage` if `readonly` is set.
    :type readonly: bool

    :param compressed: Whether to compress generated cluster zip file, file
        stored on filesystem will be gzipped, default is ``False``.
    :type compressed: bool

    :param splitter: A :class:`~stonemason.provider.tilestorage.Splitter` instance
        to split `MetaTile` data into `Tile` data.
    :type splitter: :class:`~stonemason.provider.tilestorage.Splitter`
    """

    def __init__(self, root='.', dir_mode='hilbert', pyramid=None, format=None,
                 readonly=False, compressed=False, splitter=None):
        assert isinstance(root, six.string_types)
        if not isinstance(format, FormatBundle):
            raise TileStorageError('Must specify format explicitly.')
        if not os.path.isabs(root):
            raise TileStorageError('Only accepts an absolute path.')

        storage = DiskStorage()

        key_mode = create_key_mode(dir_mode, sep=os.sep)
        object_persistence = TileClusterSerializer(compressed=compressed,
                                                   writer=format.writer)

        StorageMixin.__init__(self, storage, object_persistence, key_mode,
                              pyramid=pyramid, prefix=root,
                              mimetype=format.tile_format.mimetype,
                              extension='.zip',
                              gzip=False, readonly=readonly)
