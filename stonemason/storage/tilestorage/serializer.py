# -*- encoding: utf-8 -*-

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
class MetaTileSerializerConcept(ObjectSerializeConcept):  # pragma: no cover
    """"""
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
