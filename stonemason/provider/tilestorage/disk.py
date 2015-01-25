# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/23/15'

import os
import io
import gzip
import errno
import tempfile
import sys

from stonemason.provider.pyramid import MetaTileIndex, MetaTile, \
    Hilbert, Legacy, Pyramid

from .cluster import guess_extension, TileCluster
from .tilestorage import ClusterStorage, \
    TileStorageError, InvalidMetaTile, InvalidMetaTileIndex


def hilbert_path_mode(self, prefix, index, extension):
    dirs = [prefix]
    dirs.extend(Hilbert.coord2dir(index.z, index.x, index.y))
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    os.pathsep
    return '/'.join(dirs)


def legacy_path_mode(self, prefix, index, extension):
    dirs = [prefix]
    dirs.extend(Legacy.coord2dir(index.z, index.x, index.y))
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    return '/'.join(dirs)


def simple_path_mode(self, prefix, index, extension):
    dirs = [prefix]
    dirs.extend([str(index.z), str(index.x), str(index.y)])
    dirs.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                   index.stride, extension))
    return '/'.join(dirs)


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


class DiskClusterStorage(ClusterStorage):
    """Store TileCluster on a filesystem (disk).


    Parameters:

    `prefix`
        Root directory of the storage, will be created if its not already exists.
        Must be a writable path if the storage is not in `readonly` mode.

    `pyramid`
        The :class:`~stonemason.provider.pyramid.Pyramid` of the storage
        describes tile pyramid model.

    `mimetype`
        Mimetype of MetaTiles stored in this storage, default value is
        ``application/data``.  Mimetype of MetaTiles put into the storage
        must match storage mimetype.

    `extension`
        Filename extension used by storage, by default, its guessed from
        `mimetype`.

    `pathmode`
        How directories names are calculated from metatile coordinate.

        `simple`
            same as the tile api url schema, ``z/x/y.ext``.

        `hilbert`
            generate a hashed directory tree using Hilbert Curve.

        `legacy`
            path mode used by old `mason` codebase.

        `leagacy` and `hilbert` will limit files and subdirs under a directory
        by calculating a "hash" string from tile coordinate.
        The directory tree structure also groups  adjacent geographical
        items together, improves filesystem cache performance.

    `compressed`
        Whether the cluster zip file will be compressed, default is ``False``.

    `readonly`
        Whether set the storage in readonly mode, default is ``False``

    :param prefix: Root directory of the storage.
    :param pyramid: Pyramid model of the storage.
    :param mimetype: Mimetype of MetaTiles.
    :param extension: Optional file extension in ``.ext``.
    :param pathmode: How pathname is calculated from tile coordinate.
    :param compressed: Whether to compress the zip file.
    :param splitter:
    """

    def __init__(self,
                 prefix='',
                 pyramid=None,
                 mimetype='application/data',
                 extension=None,
                 pathmode='hilbert',
                 compressed=False,
                 readonly=False,
                 splitter=None):

        assert isinstance(prefix, six.string_types)
        assert isinstance(pyramid, Pyramid)

        self._prefix = prefix

        self._pyramid = pyramid

        if extension is None:
            self._extension = guess_extension(mimetype)
        else:
            self._extension = extension

        self._pathmode = PATH_MODES[pathmode]

        self._compressed = compressed

        self._use_gzip = False
        if self._use_gzip:
            self._extension = self._extension + '.gz'

        self._readonly = readonly

    def retrieve(self, pathname):
        if not os.path.exists(pathname):
            # not exist
            return None

        if self._use_gzip:
            fp = gzip.GzipFile(pathname, 'rb')
        else:
            fp = open(pathname, 'rb')

        mtime = os.stat(pathname).st_mtime
        return fp, dict(mimetype=None, mtime=mtime, etag=None)

    def store(self, pathname, blob, metadata):
        dirname, basename = os.path.split(pathname)

        # create directory first
        if not (os.path.exists(pathname) and os.path.isdir(pathname)):
            safe_makedirs(dirname)

        # generate temp file name
        tempname = None
        for n, temp in enumerate(tempfile._get_candidate_names()):
            tempname = os.path.join(dirname, '%s~%s' % (basename, temp))
            if n >= tempfile.TMP_MAX:
                raise TileStorageError('Exhausted temp file name')

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

    def get(self, index):
        assert isinstance(index, MetaTileIndex)
        pathname = self._pathmode(self._prefix, index, self._extension)
        blob, metadata = self.retrieve(pathname)
        return TileCluster.from_zip(blob, metadata=metadata)

    def put(self, metatile):
        assert isinstance(metatile, MetaTile)
        pathname = self._pathmode(self._prefix, metatile.index, self._extension)
        metadata = dict(mimetype=metatile.mimetype,
                        mtime=metatile.mtime,
                        etag=metatile.etag)

        TileCluster.from_metatile()
        self.store(pathname, metatile.data, metadata)

    def retire(self, index):
        pathname = self._pathmode(self._prefix, index, self._extension)
        try:
            os.unlink(pathname)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # file not found, ignore
                pass
            else:
                raise
