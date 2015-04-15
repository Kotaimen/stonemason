# -*- encoding: utf-8 -*-

"""
    stonemason.provider.tilestorage.cluster
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Metatile split into Tiles.
"""

__author__ = 'kotaimen'
__date__ = '1/18/15'

import collections
import zipfile
import json
import math

import six

from stonemason.util.guesstypes import guess_mimetype, guess_extension
from stonemason.pyramid import Tile, TileIndex, MetaTile, MetaTileIndex
from stonemason.provider.formatbundle import MapWriter
from .exceptions import TileClusterError



# The index file name
CLUSTER_ZIP_INDEX = 'index.json'
CLUSTER_ZIP_INDEX_LEGACY = 'tiles.json'
CLUSTER_ZIP_VERSION = 1


class TileCluster(object):
    """A cluster of `Tiles` split from  a `MetaTile`.

    `TileCluster` can be loaded from a clustered zip file or created from
    `MetaTile`.


    >>> from stonemason.provider.tilestorage import TileCluster
    >>> from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
    >>> from stonemason.pyramid import MetaTile, MetaTileIndex, TileIndex
    >>> from PIL import Image
    >>> import io
    >>> image = Image.new('RGB', (1024, 1024))
    >>> buffer = io.BytesIO()
    >>> image.save(buffer, 'JPEG')
    >>> image_data = buffer.getvalue()
    >>> metatile = MetaTile(MetaTileIndex(4, 4, 8, 2),
    ...                     data=image_data,
    ...                     mimetype='image/jpeg',
    ...                     mtime=1.,
    ...                     buffer=256)
    >>> format_bundle = FormatBundle(MapType('image'), TileFormat('JPEG'))
    >>> cluster = TileCluster.from_metatile(metatile, format_bundle.writer)
    >>> cluster.index
    MetaTileIndex(4/4/8@2)
    >>> cluster.tiles
    [Tile(4/4/8), Tile(4/4/9), Tile(4/5/8), Tile(4/5/9)]
    >>> cluster[TileIndex(4, 4, 8)]
    Tile(4/4/8)

    :param index: Metatile index of this cluster.
    :type index: :class:`~stonemason.provider.MetaTileIndex`.
    :param tiles: Tiles of this cluster
    :type index: :class:`~stonemason.provider.Tile`.
    """

    def __init__(self, index, tiles):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(tiles, list)
        self._index = index
        self._tiles = sorted(tiles,
                             key=lambda tile: self._tile_key_func(tile.index))

    def _tile_key_func(self, index):
        return (index.x - self._index.x) * self._index.stride + \
               (index.y - self._index.y)

    @property
    def index(self):
        """:class:`~stonemason.provider.MetaTileIndex` of this cluster."""
        return self._index

    @property
    def tiles(self):
        """A list of :class:`~stonemason.provider.Tile` in this cluster."""
        return self._tiles

    def __getitem__(self, index):
        """Retrieve `Tile` with given index

        :param index: Index of the tile.
        :type index: :class:`~stonemason.provider.MetaTileIndex`
        :return: Tile
        :rtype: :class:`~stonemason.provider.Tile`
        :raise: :class:`~TileClusterError`
        """
        assert isinstance(index, TileIndex)
        if MetaTileIndex.from_tile_index(index,
                                         self._index.stride) != self._index:
            raise TileClusterError('Tile index is not covered in the cluster.')

        row, column = index.x - self.index.x, index.y - self.index.y
        return self._tiles[self._tile_key_func(index)]


    @staticmethod
    def from_metatile(metatile, writer):
        """Create a `TileCluster` object from a `MetaTile`.

        Besides `metatile`, a :class:`~stonemason.provider.formatbundle.MapWriter`
        instance must also be provided.  It is used to re-split metatile
        data into smaller tiles.

        :param metatile: The metatile.
        :type metatile: :class:`~stonemason.tilecache.TileCluster`

        :param writer: A `MapWriter` to resplit metatile data into small tiles.
        :type writer: :class:`~stonemason.provider.formatbundle.MapWriter`

        :return: created cluster object.
        :rtype: :class:`~stonemason.provider.tilestorage.TileCluster`
        """
        assert isinstance(metatile, MetaTile)
        assert isinstance(writer, MapWriter)

        # calculate (row, column) index to relative left top tile
        tile_indexes = dict()
        for tile_index in metatile.index.fission():
            row = tile_index.x - metatile.index.x
            column = tile_index.y - metatile.index.y
            tile_indexes[(row, column)] = tile_index

        # reference tile index using split tile data
        tiles = list()
        for (row, column), data in writer.resplit_map(metatile.data,
                                                      metatile.index.stride,
                                                      metatile.buffer):
            tile = Tile(tile_indexes[(row, column)],
                        data,
                        mimetype=metatile.mimetype,
                        mtime=metatile.mtime)
            tiles.append(tile)

        return TileCluster(metatile.index, tiles)

    @staticmethod
    def from_image(index, image, metadata, writer=None, buffer=0):
        # XXX not necessary till we have real rendering
        raise NotImplementedError

    @staticmethod
    def from_zip(zip_file, metadata=None):
        """Load `TileCluster` from a clustered zip file.

        :param zip_file: The zip file, can be a file name or a file like object.
        :type zip_file: FileIO
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

            # if mimetype is not provided in the index, guess from extension
            try:
                mimetype = index['mimetype']
            except KeyError:
                mimetype = guess_mimetype(extension)
            if metadata is not None and 'mimetype' in metadata and metadata['mimetype'] is not None:
                if metadata['mimetype'] != mimetype:
                    raise TileClusterError('Mismatching mimetype: expecting "%s", got "%s".' % (metadata['mimetype'], mimetype ))

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
            assert stride & (stride - 1) == 0

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

        keys = list('%d-%d-%d' % tile.index for tile in self._tiles)
        hashes = list(tile.etag for tile in self._tiles)
        datas = list(tile.data for tile in self._tiles)

        # key->data map for index.json
        mapping = dict(zip(keys, datas))

        # build a key->key dict and delete duplicated tile data
        dedup = dict()
        for i in range(len(self._tiles)):
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
            sample_tile = self._tiles[0]  # XXX: should check all tiles
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
