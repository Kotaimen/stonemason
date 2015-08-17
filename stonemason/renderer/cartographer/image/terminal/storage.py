# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/3/15'

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from PIL import Image

from stonemason.renderer.engine.rendernode import TermNode
from stonemason.renderer.engine.context import RenderContext
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.tilestorage import MetaTileStorage, DiskMetaTileStorage, \
    S3MetaTileStorage

from ..feature import ImageFeature

__all__ = ['S3StorageNode', 'DiskStorageNode']


class _MetaTileStorageNode(TermNode):
    def __init__(self, name, storage):
        TermNode.__init__(self, name)
        assert isinstance(storage, MetaTileStorage)

        self._storage = storage

    def render(self, context):
        assert isinstance(context, RenderContext)

        meta_index = context.meta_index

        meta_tile = self._storage.get(meta_index)
        if meta_tile is None:
            raise RuntimeError(
                '[%s] MetaTile %s not found!' % (self.name, meta_index))

        stream = StringIO.StringIO(meta_tile.data)
        pil_image = Image.open(stream)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature


class DiskStorageNode(_MetaTileStorageNode):
    def __init__(self, name, **kwargs):
        parameters = dict(kwargs)

        maptype = MapType(parameters.pop('maptype', 'image'))

        try:
            tileformat = parameters.pop('tileformat', dict())
        except KeyError:
            raise ValueError('Must specify "tileformat" for storage layer.')
        bundle = FormatBundle(maptype, TileFormat(**tileformat))

        storage = DiskMetaTileStorage(format=bundle, **parameters)

        _MetaTileStorageNode.__init__(self, name, storage)


class S3StorageNode(_MetaTileStorageNode):
    def __init__(self, name, **kwargs):
        parameters = dict(kwargs)

        maptype = MapType(parameters.pop('maptype', 'image'))

        try:
            tileformat = parameters.pop('tileformat')
        except KeyError:
            raise ValueError('Must specify "tileformat" for storage layer.')
        bundle = FormatBundle(maptype, TileFormat(**tileformat))

        storage = S3MetaTileStorage(format=bundle, **parameters)

        _MetaTileStorageNode.__init__(self, name, storage)
