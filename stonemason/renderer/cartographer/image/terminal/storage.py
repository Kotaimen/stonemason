# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.terminal.storage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of storage render nodes.
"""
__author__ = 'ray'
__date__ = '8/3/15'

from io import BytesIO

from PIL import Image

from stonemason.renderer.engine.rendernode import TermNode
from stonemason.renderer.engine.context import RenderContext
from stonemason.formatbundle import FormatBundle, MapType, TileFormat
from stonemason.storage import MetaTileStorageConcept, DiskMetaTileStorage, \
    S3MetaTileStorage

from ..feature import ImageFeature

__all__ = ['S3StorageNode', 'DiskStorageNode']


class _MetaTileStorageNode(TermNode):
    """Base Class of MetaTile Storage Render Node

    :param name: a string literal that identifies the node.
    :type name: str

    :param storage: instance of metatile storage.
    :type storage: :class:`~stonemason.tilestorage.MetaTileStorage`

    """
    def __init__(self, name, storage):
        TermNode.__init__(self, name)
        assert isinstance(storage, MetaTileStorageConcept)

        self._storage = storage

    def render(self, context):
        """Render a image feature.

        :param context: requirements and conditions for feature rendering.
        :type context: :class:`~stonemason.renderer.engine.RenderContext`

        :return: a image feature.
        :rtype: :class:`~stonemason.renderer.cartographer.image.ImageFeature`

        """
        assert isinstance(context, RenderContext)

        meta_index = context.meta_index

        meta_tile = self._storage.get(meta_index)
        if meta_tile is None:
            return None

        stream = BytesIO(meta_tile.data)
        pil_image = Image.open(stream)

        feature = ImageFeature(crs=context.map_proj,
                               bounds=context.map_bbox,
                               size=context.map_size,
                               data=pil_image)

        return feature


class DiskStorageNode(_MetaTileStorageNode):
    """Disk MetaTile Storage Render Node

    :param name: a string literal that identifies the node.
    :type name: str

    :param kwargs: parameters for setting up :class:`stonemason.tilestorage.DiskMetaTileStorage`.
    :type kwargs: dict

    """
    def __init__(self, name, **kwargs):
        parameters = dict(kwargs)

        maptype = MapType(parameters.pop('maptype', 'image'))
        tileformat = parameters.pop('tileformat', dict())
        bundle = FormatBundle(maptype, TileFormat(**tileformat))

        storage = DiskMetaTileStorage(format=bundle, **parameters)

        _MetaTileStorageNode.__init__(self, name, storage)


class S3StorageNode(_MetaTileStorageNode):
    """S3 MetaTile Storage Render Node

    :param name: a string literal that identifies the node.
    :type name: str

    :param kwargs: parameters for setting up :class:`stonemason.tilestorage.S3MetaTileStorage`.
    :type kwargs: dict

    """
    def __init__(self, name, **kwargs):
        parameters = dict(kwargs)

        maptype = MapType(parameters.pop('maptype', 'image'))
        tileformat = parameters.pop('tileformat', dict())
        bundle = FormatBundle(maptype, TileFormat(**tileformat))

        storage = S3MetaTileStorage(format=bundle, **parameters)

        _MetaTileStorageNode.__init__(self, name, storage)
