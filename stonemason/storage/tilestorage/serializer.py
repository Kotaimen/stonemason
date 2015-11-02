# -*- encoding: utf-8 -*-
"""
    stonemason.storage.tilestorage.serializer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements metatile serializer.
"""
__author__ = 'ray'
__date__ = '10/26/15'

import io
import gzip

from stonemason.formatbundle import MapWriter
from stonemason.pyramid import MetaTileIndex, MetaTile, TileCluster

from ..concept import ObjectSerializeConcept

from .errors import InvalidMetaTile


# ==============================================================================
# MetaTile Serializer
# ==============================================================================
class MetaTileSerializeConcept(ObjectSerializeConcept):  # pragma: no cover
    """MetaTile Serializer Concept"""
    pass


class MetaTileSerializer(MetaTileSerializeConcept):
    """MetaTile Serializer

    The ``MetaTileSerializer`` implements details of how a metatile is
    serialized to a binary data and how it is recovered from a binary dump.

    :param gzip: Whether compress or decompress data.
    :type gzip: bool

    :param mimetype: Mimetype of the metatile data.
    :type mimetype: str

    """

    def __init__(self, gzip=False, mimetype='image/png'):
        self._use_gzip = bool(gzip)
        self._mimetype = mimetype

    def load(self, index, blob, metadata):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(metadata, dict)

        if self._use_gzip:
            # decompress gzip
            blob = gzip.GzipFile(fileobj=io.BytesIO(blob), mode='rb').read()

        attributes = {}
        attributes['etag'] = metadata.get('etag')
        attributes['mimetype'] = metadata.get('mimetype', self._mimetype)
        attributes['mtime'] = float(metadata.get(
            'mtime', metadata.get('LastModified')))

        return MetaTile(index, data=blob, **attributes)

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
            mtime=str(obj.mtime),
            etag=obj.etag)

        return blob, metadata


class TileClusterSerializer(MetaTileSerializeConcept):
    """TileCluster Serializer

    The ``TileClusterSerializer`` dumps a metatile into a binary data in
    TileCluster format and load a TileCluster from a binary data.

    The dumped object is metatile while the recovered object is tilecluster.

    :param writer: The Serializer that convert metatile into binary data in the
                   format of cluster tile.

    :type writer: :class:`~stonemason.formatbundle.MapWriter`

    :param compressed: Whether compress or decompress the data.
    :type compressed: bool

    :param mimetype: Mimetype of the metatile data.
    :type mimetype: str

    """

    def __init__(self, writer, compressed=False, mimetype='image/png'):
        assert isinstance(writer, MapWriter)
        self._compressed = compressed
        self._writer = writer
        self._mimetype = mimetype

    def load(self, index, blob, metadata):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(metadata, dict)

        # let tilecluster figure out mimetype from cluster index,
        # since storage always assign 'application/zip' for a cluster
        attributes = {}
        attributes['mtime'] = float(metadata.get(
            'mtime', metadata.get('LastModified')))

        return TileCluster.from_zip(io.BytesIO(blob), metadata=attributes)

    def save(self, index, obj):
        assert isinstance(index, MetaTileIndex)
        assert isinstance(obj, MetaTile)

        if obj.mimetype != self._mimetype:
            raise InvalidMetaTile('MetaTile mimetype inconsistent with storage')

        metadata = dict(mimetype='application/zip',
                        mtime=str(obj.mtime),
                        etag=obj.etag)
        cluster = TileCluster.from_metatile(obj, self._writer)
        buf = io.BytesIO()
        cluster.save_as_zip(buf, compressed=self._compressed)
        return buf.getvalue(), metadata
