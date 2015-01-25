# -*- encoding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

__author__ = 'kotaimen'
__date__ = '1/18/15'

"""
    stonemason.provider.tilestorage.cluster
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Metatile split into Tiles.
"""

import collections
import zipfile
import json
import mimetypes
import math

import six

from stonemason.util.postprocessing.gridcrop import grid_crop_into_data

from stonemason.provider.pyramid import Tile, TileIndex, MetaTile, \
    MetaTileIndex

from .tilestorage import TileStorageError


class TileClusterError(TileStorageError):
    pass


class Splitter(object):  # pragma: no cover
    """Base class for metatile data splitter."""

    def __call__(self, data, stride, buffer):
        """Crop given metatile data into smaller tile data.

        :param data: Metatile data.
        :type data: bytes
        :param stride: Number of tiles per axis.
        :type stride: int
        :param buffer: Size of pixel buffer around metatile.
        :type buffer: int
        :return: A iterable of ``((row, column), grid_data)``.
        :rtype: iterator
        """
        raise NotImplementedError


class ImageSplitter(Splitter):
    """Split metatile using grid cropper and provided format and parameters.

    Split given metatile image data into tiles by calling grid cropping.

    .. seealso:: :func:`~stonemason.util.postprocessing.gridcrop.grid_crop_into_data` and
        :func:`~stonemason.util.postprocessing.gridcrop.grid_crop`

    >>> from stonemason.provider.tilestorage import ImageSplitter
    >>> from PIL import Image
    >>> import io
    >>> image = Image.new('RGB', (768, 768))
    >>> splitter = ImageSplitter(format='JPEG',
    ...                          parameters={'optimized':True,
    ...                                      'quality': 60})
    >>> for (row, column), image_data in splitter(image, 2, 128):
    ...     grid_image = Image.open(io.BytesIO(image_data))
    ...     print grid_image.format, grid_image.size
    JPEG (256, 256)
    JPEG (256, 256)
    JPEG (256, 256)
    JPEG (256, 256)

    :param format: Format of the cropped tile data.
    :param parameters: Image save format parameters.
    """

    def __init__(self, format=None, parameters=None):
        if parameters is None:
            parameters = {}
        self._format = format
        self._parameters = parameters

    def __call__(self, data, stride, buffer):
        return grid_crop_into_data(data,
                                   stride=stride,
                                   buffer_size=buffer,
                                   format=self._format,
                                   parameters=self._parameters)

# The index file name
CLUSTER_ZIP_INDEX = 'index.json'
CLUSTER_ZIP_INDEX_LEGACY = 'tiles.json'
CLUSTER_ZIP_VERSION = 1


def guess_extension(mimetype):
    """Guess extension from mimetype, return empty string on failure.

    :func:`mimetype.guess_extension` sometimes returns different value on
    python2 and python3::

        $ python -c 'import mimetypes; print(mimetypes.guess_extension("image/tiff"))'
        .tif
        $ python3 -c 'import mimetypes; print(mimetypes.guess_extension("image/tiff"))'
        .tiff

    """
    if mimetype is None:
        return ''

    if mimetype == 'application/data':
        return '.dat'
    elif mimetype in ['image/jpg', 'image/jpeg']:
        return '.jpg'
    elif mimetype == 'image/tiff':
        return '.tif'
    elif mimetype == 'text/plain':
        return '.txt'

    ext = mimetypes.guess_extension(mimetype)

    if ext is None:
        return ''
    else:
        return ext


def guess_mimetype(extension):
    """Guess mimetype from extension, return ``application/data`` on failure.
    """

    if extension is None:
        return 'application/data'

    mimetype, encoding = mimetypes.guess_type('foo' + extension)

    if mimetype is None:
        return 'application/data'
    else:
        return mimetype


class TileCluster(collections.namedtuple('_TileCluster', 'index tiles')):
    """A cluster of `Tiles` split from  a `MetaTile`.

    `TileCluster` is the base storage unit of `ClusterStorage`.

    Properties:

    `index`
        :class:`~stonemason.provider.MetaTileIndex` of this cluster.

    `tiles`
        List of :class:`~stonemason.provider.Tile`s in this cluster.
    """

    @staticmethod
    def from_metatile(metatile, splitter=None):
        """Create a `TileCluster` object from a `MetaTile`.

        Besides `metatile`, a :class:`~stonemason.provider.tilestorage.Splitter`
        instance must also be provided.  The splitter is used to split metatile
        data into smaller tiles.

        To split a raster image tile, use included
        :class:`~stonemason.provider.tilestorage.ImageSplitter` class.

        :param metatile: The metatile.
        :type metatile: :class:`~stonemason.provider.tilecache.TileCluster`
        :param splitter: A splitter to tansform metatile data into small tiles.
        :type splitter: Splitter
        :return: created cluster object.
        :rtype: :class:`~stonemason.provider.tilestorage.TileCluster`
        """
        assert isinstance(metatile, MetaTile)

        if splitter is None and metatile.mimetype.startswith('image/'):
            splitter = ImageSplitter()
        assert isinstance(splitter, Splitter)

        # calculate (row, column) index to relative left top tile
        tile_indexes = dict()
        for tile_index in metatile.index.fission():
            row = tile_index.x - metatile.index.x
            column = tile_index.y - metatile.index.y
            tile_indexes[(row, column)] = tile_index

        # reference tile index using split tile data
        tiles = list()
        for (row, column), data in splitter(metatile.data,
                                            metatile.index.stride,
                                            metatile.buffer):
            tile = Tile(tile_indexes[(row, column)],
                        data,
                        mimetype=metatile.mimetype,
                        mtime=metatile.mtime)
            tiles.append(tile)

        return TileCluster(metatile.index, tiles)

    @staticmethod
    def from_zip(zip_file, metadata=None):
        """Load `TileCluster` from a clustered zip file.

        :param zip_file: The zip file, can be a file name or a file like object.
        :type zip_file: file
        :param metadata: Extra metadata as a dict, overwriting any metadata
                         in the zip file.
        :type metadata: dict
        :return: Created cluster object.
        :rtype: :class:`~stonemason.provider.tilestorage.TileCluster`
        :raises: :class:`~stonemason.provider.tilestorage.TileClusterError`
        """

        try:
            zip_file = zipfile.ZipFile(file=zip_file, mode='r')

            # decode the metadata
            try:
                index_file_info = zip_file.getinfo(CLUSTER_ZIP_INDEX)
            except KeyError:
                # try legacy index file name again
                index_file_info = zip_file.getinfo(CLUSTER_ZIP_INDEX_LEGACY)

            index = json.loads(zip_file.read(index_file_info).decode('utf-8'))

            # read required fields
            tile_datas = index['datas']
            tile_indexes = index['tiles']
            extension = index['extension']

            # load optional fields
            def load_optional_field(fieldname):
                if metadata is not None and fieldname in metadata:
                    field = metadata[fieldname]
                elif fieldname in index:
                    field = index[fieldname]
                else:
                    field = None
                if six.PY2:
                    if isinstance(field, unicode):
                        # make sure fields values are *not* unicode under py27
                        field = field.encode('ascii')
                return field

            mimetype = load_optional_field('mimetype')
            if mimetype is None:
                mimetype = guess_mimetype(extension)
            mtime = load_optional_field('mtime')

            # load tile datas
            datas = dict()
            for k in tile_datas:
                datas[k] = zip_file.read(k + extension)

            # create tile object
            tiles = list()
            for k, v in six.iteritems(tile_indexes):
                z, x, y = tuple(map(int, k.split('-')))
                tile = Tile(TileIndex(z, x, y),
                            datas[v],
                            mimetype=mimetype,
                            mtime=mtime)
                tiles.append(tile)

            # calculate stride from number of indexes
            stride = load_optional_field('stride')
            if stride is None:
                stride = int(math.sqrt(len(tile_indexes)))
            assert stride & ( stride - 1 ) == 0

            # recreate the metatile index from any tile
            sample_tile = tiles[0]
            # XXX: should do some validation here on MetaTileIndex
            metatile_index = MetaTileIndex(sample_tile.index.z,
                                           sample_tile.index.x,
                                           sample_tile.index.y,
                                           stride)

            return TileCluster(metatile_index, tiles)

        except Exception as e:
            raise  # TileClusterError(repr(e))

    def save_as_zip(self, zip_file, compressed=False):
        """Save `TileCluster` as a zip file.

        .. note::
            The `compress` parameter has no real effect on most
            raster image types, since they are already compressed.
            ``index.json`` can be compressed but the save on space is
            not worth extra CPU cycle.

        :param zip_file: A file object points to the zip file.
        :param compressed: Whether to compress zip file, default is ``False``.
        :raises: :class:`~stonemason.provider.tilestorage.TileClusterError`
        """

        keys = list('%d-%d-%d' % tile.index for tile in self.tiles)
        hashes = list(tile.etag for tile in self.tiles)
        datas = list(tile.data for tile in self.tiles)

        # key->data map for index.json
        mapping = dict(zip(keys, datas))

        # build a key->key dict and delete duplicated tile data
        dedup = dict()
        for i in range(len(self.tiles)):
            k = keys[i]
            h = hashes[i]
            try:
                # use first data of indexes which have same hash
                j = hashes[0:i].index(h)
                dedup[k] = keys[j]
                del mapping[k]
            except ValueError:
                dedup[k] = k

        # write zipfile in memory as buffer
        compression = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED

        with zipfile.ZipFile(file=zip_file, mode='w',
                             compression=compression) as zipobj:

            # build index.json
            sample_tile = self.tiles[0]  # XXX: should check all tiles
            extension = guess_extension(sample_tile.mimetype)
            # try keep json dump ordered
            index = collections.OrderedDict([
                ('version', CLUSTER_ZIP_VERSION),
                ('tiles', dedup),
                ('datas', list(six.iterkeys(mapping))),
                ('extension', extension),
                ('mimetype', sample_tile.mimetype),
                ('stride', self.index.stride),
                ('mtime', sample_tile.mtime,)
            ])

            zipobj.writestr(CLUSTER_ZIP_INDEX, json.dumps(index, indent=2))
            for k, data in six.iteritems(mapping):
                zipobj.writestr(k + extension, data)
