# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/23/15'

"""
    stonemason.provider.tilestorage.disk
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Disk based storages.

"""

# TODO: Refactor this after s3 storage is completed.

import os
import io
import gzip
import errno
import sys

import six

from stonemason.provider.pyramid import MetaTileIndex, MetaTile, \
    Hilbert, Legacy, Pyramid

from stonemason.util.guesstypes import guess_extension, guess_mimetype
from stonemason.util.tempfn import generate_temp_filename

from .cluster import TileCluster
from .tilestorage import ClusterStorage, MetaTileStorage, \
    TileStorageError, InvalidMetaTile, InvalidMetaTileIndex, ReadonlyStorage


def hilbert_path_mode(prefix, index, extension):
    dirs = [prefix]
    dirs.extend(Hilbert.coord2dir(index.z, index.x, index.y))
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    return os.sep.join(dirs)


def legacy_path_mode(prefix, index, extension):
    dirs = [prefix]
    dirs.extend(Legacy.coord2dir(index.z, index.x, index.y))
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    return os.sep.join(dirs)


def simple_path_mode(prefix, index, extension):
    dirs = [prefix]
    dirs.extend([str(index.z), str(index.x), str(index.y)])
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    return os.sep.join(dirs)


PATH_MODES = dict(
    simple=simple_path_mode,
    legacy=legacy_path_mode,
    hilbert=hilbert_path_mode,
)


def safe_makedirs(name, mode=0o0777):
    try:
        os.makedirs(name, mode)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # Ignore "already exists" error because os.makedirs
            # does not check dir exists at each creation step
            pass
        else:
            raise


class DiskStorageMixin(object):
    """Implement common disk storage features."""

    def __init__(self,
                 pyramid=None,
                 mimetype='application/data',
                 extension=None,
                 pathmode='hilbert',
                 gzip=False,
                 readonly=False,
                 prefix='.'):

        # prefix
        assert isinstance(prefix, six.string_types)
        assert os.path.isabs(prefix)
        self._prefix = prefix

        # tile pyramid
        assert isinstance(pyramid, Pyramid)
        self._pyramid = pyramid

        # guess extension from mimetype
        if extension is None:
            self._extension = guess_extension(mimetype)
        else:
            assert extension.startswith('.')
            self._extension = extension
        self._mimetype = mimetype

        # select pathmode
        self._pathmode = PATH_MODES[pathmode]

        self._readonly = readonly

        self._use_gzip = gzip
        if self._use_gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'


    def _retrieve(self, pathname):
        if not os.path.exists(pathname):
            # not exist
            return None, None

        if self._use_gzip:
            fp = gzip.GzipFile(pathname, 'rb')
        else:
            fp = open(pathname, 'rb')
        with fp:
            blob = fp.read()

        mtime = os.stat(pathname).st_mtime
        return blob, dict(mimetype=None, mtime=mtime, etag=None)

    def _store(self, pathname, blob, metadata):
        if self._readonly:
            raise ReadonlyStorage
        dirname, basename = os.path.split(pathname)

        # create directory first
        if not (os.path.exists(pathname) and os.path.isdir(pathname)):
            safe_makedirs(dirname)

        # generate temp file name
        tempname = generate_temp_filename(dirname, prefix=basename)

        # write the file
        if self._use_gzip:
            with gzip.GzipFile(tempname, 'wb') as fp:
                fp.write(blob)
        else:
            with open(tempname, 'wb') as fp:
                fp.write(blob)

        # move it into place
        if sys.platform == 'win32':
            if os.path.exists(pathname):
                # os.rename is not atomic on windows
                os.remove(pathname)
        os.rename(tempname, pathname)

    def _delete(self, pathname):
        if self._readonly:
            raise ReadonlyStorage
        try:
            os.unlink(pathname)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # file not found, ignore
                pass
            else:
                raise


class DiskClusterStorage(ClusterStorage, DiskStorageMixin):
    """Store TileCluster on a filesystem (disk).


    Parameters:

    `pyramid`
        The :class:`~stonemason.provider.pyramid.Pyramid` of the storage
        describes tile pyramid model.

    `mimetype`
        Mimetype of MetaTiles stored in this storage, default value is
        ``application/data``.  MetaTiles put into the storage must match
        storage mimetype.

    `pathmode`
        How directories names are calculated from metatile coordinate.

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        `legacy` and `hilbert` will limit files and subdirs under a directory
        by calculating a "hash" string from tile coordinate.
        The directory tree structure also groups adjacent geographical
        items together, improves filesystem cache performance.

    `readonly`
        Whether to set the storage in readonly mode, default is ``False``.

    `prefix`
        Root directory of the storage, will be created if its not already exists.
        Must be a writable path if the storage is not in `readonly` mode.

    `compressed`
        Whether the cluster zip file will be compressed, default is ``False``.

    `splitter`
        :class:`~stonemason.provider.tilestorage.Splitter` used to split meta
        tile data, default is to use :class:`~stonemason.provider.tilestorage.ImageSplitter`
        if `mimetype` is a raster image.

    :param pyramid: Pyramid model of the storage.
    :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`
    :param mimetype: Mimetype of meta tile.
    :type mimetype: str
    :param pathmode: How pathname is calculated from tile coordinate.
    :type pathmode: str
    :param readonly: Whether the storage is read only.
    :type readonly: bool
    :param prefix: Root directory of the storage.
    :type prefix: str
    :param compressed: Whether to compress the zip file.
    :type compressed: bool
    :param splitter: meta tile splitter.
    :type splitter: :class:`~stonemason.provider.tilestorage.Splitter`
    """

    def __init__(self,
                 pyramid=None,
                 mimetype='application/data',
                 pathmode='hilbert',
                 readonly=False,
                 prefix='.',
                 compressed=False,
                 splitter=None):
        DiskStorageMixin.__init__(self,
                                  pyramid=pyramid,
                                  mimetype=mimetype,
                                  extension=None,
                                  pathmode=pathmode,
                                  gzip=False,
                                  readonly=readonly,
                                  prefix=prefix)
        self._extension = '.zip'  # force use zip as extension
        self._splitter = splitter
        self._compressed = compressed

    def get(self, index):
        assert isinstance(index, MetaTileIndex)
        pathname = self._pathmode(self._prefix, index, self._extension)
        blob, metadata = self._retrieve(pathname)
        if blob is None:
            return None
        else:
            # XXX: Its ugly to wrap blob with BytesIO, considering passing fp here?
            return TileCluster.from_zip(io.BytesIO(blob), metadata=metadata)

    def put(self, metatile):
        assert isinstance(metatile, MetaTile)
        if metatile.index.z not in self._pyramid.levels:
            raise InvalidMetaTileIndex('MetaTile level not defined in Pyramid.')
        if metatile.index.stride != self._pyramid.stride:
            raise InvalidMetaTileIndex(
                'MetaTile stride incompatible with storage.')

        if metatile.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        pathname = self._pathmode(self._prefix, metatile.index, self._extension)
        metadata = dict(mimetype=metatile.mimetype,
                        mtime=metatile.mtime,
                        etag=metatile.etag)

        cluster = TileCluster.from_metatile(metatile, self._splitter)
        buf = io.BytesIO()
        cluster.save_as_zip(buf, compressed=self._compressed)
        self._store(pathname, buf.getvalue(), metadata)

    def retire(self, index):
        pathname = self._pathmode(self._prefix, index, self._extension)
        self._delete(pathname)


class DiskMetaTileStorage(MetaTileStorage, DiskStorageMixin):
    """Store MetaTile on a filesystem (disk).

    Parameters:

    `pyramid`
        The :class:`~stonemason.provider.pyramid.Pyramid` of the storage
        describes tile pyramid model.

    `mimetype`
        Mimetype of MetaTiles stored in this storage, default value is
        ``application/data``.  MetaTiles put into the storage must match
        storage mimetype.

    `extension`
        Filename extension used by storage, by default, its guessed from
        `mimetype`.

    `pathmode`
        How directories names are calculated from metatile coordinate.

        `simple`
            Same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            Generate a hashed directory tree using Hilbert Curve.

        `legacy`
            Path mode used by old `mason` codebase.

        `legacy` and `hilbert` will limit files and subdirs under a directory
        by calculating a "hash" string from tile coordinate.
        The directory tree structure also groups  adjacent geographical
        items together, improves filesystem cache performance.

    `gzip`
        Whether to use gzip to compress written data, default is ``False``.
        Note if `gzip` is enabled, ``.gz`` will be appended to `extension`.

    `readonly`
        Whether set the storage in readonly mode, default is ``False``.

    `prefix`
        Root directory of the storage, will be created if its not already exists.
        Must be a writable path if the storage is not in `readonly` mode.

    :param pyramid: Pyramid model of the storage.
    :type pyramid: :class:`~stonemason.provider.pyramid.Pyramid`
    :param mimetype: Mimetype of meta tile.
    :type mimetype: str
    :param extension: Optional file extension in ``.ext``.
    :type extension: str
    :param pathmode: How pathname is calculated from tile coordinate.
    :type pathmode: str
    :param readonly: Whether the storage is read only.
    :type readonly: bool
    :param gzip: Whether write data as a gzip file.
    :type gzip: bool
    :param prefix: Root directory of the storage.
    :type prefix: str
    """

    def __init__(self,
                 pyramid=None,
                 mimetype='application/data',
                 extension=None,
                 pathmode='hilbert',
                 gzip=False,
                 readonly=False,
                 prefix='.', ):
        DiskStorageMixin.__init__(self,
                                  pyramid=pyramid,
                                  mimetype=mimetype,
                                  extension=extension,
                                  pathmode=pathmode,
                                  gzip=gzip,
                                  readonly=readonly,
                                  prefix=prefix)

    def get(self, index):
        assert isinstance(index, MetaTileIndex)
        pathname = self._pathmode(self._prefix, index, self._extension)
        blob, metadata = self._retrieve(pathname)
        if blob is None:
            return None
        return MetaTile(index,
                        data=blob,
                        **metadata)

    def put(self, metatile):
        assert isinstance(metatile, MetaTile)
        if metatile.index.z not in self._pyramid.levels:
            raise InvalidMetaTileIndex('MetaTile level not defined in Pyramid.')
        if metatile.index.stride != self._pyramid.stride:
            raise InvalidMetaTileIndex(
                'MetaTile stride incompatible with storage.')
        if metatile.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        pathname = self._pathmode(self._prefix, metatile.index, self._extension)
        metadata = dict(mimetype=metatile.mimetype,
                        mtime=metatile.mtime,
                        etag=metatile.etag)
        self._store(pathname, metatile.data, metadata)

    def retire(self, index):
        pathname = self._pathmode(self._prefix, index, self._extension)
        self._delete(pathname)
