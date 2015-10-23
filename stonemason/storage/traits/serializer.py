# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

import io

from stonemason.pyramid import MetaTile, TileCluster
from stonemason.formatbundle import MapWriter

from ..concept import ObjectSerializeConcept


class MetaTileSerializer(ObjectSerializeConcept):
    def load(self, index, blob, metadata):
        return MetaTile(index, data=blob, **metadata)

    def save(self, metatile):
        metadata = dict(mimetype=metatile.mimetype,
                        mtime=metatile.mtime,
                        etag=metatile.etag)
        return metatile.data, metadata


class TileClusterSerializer(ObjectSerializeConcept):
    def __init__(self, writer, compressed=False):
        assert isinstance(writer, MapWriter)
        self._compressed = compressed
        self._writer = writer

    def load(self, index, blob, metadata):
        metadata = metadata.copy()
        # let tilecluster figure out mimetype from cluster index,
        # since storage always assign 'application/zip' for a cluster
        del metadata['mimetype']
        return TileCluster.from_zip(io.BytesIO(blob), metadata=metadata)

    def save(self, metatile):
        metadata = dict(mimetype='application/zip',
                        mtime=metatile.mtime,
                        etag=metatile.etag)
        cluster = TileCluster.from_metatile(metatile, self._writer)
        buf = io.BytesIO()
        cluster.save_as_zip(buf, compressed=self._compressed)
        return buf.getvalue(), metadata
