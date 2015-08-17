# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/14/15'

from stonemason.renderer.engine.factory import RenderNodeFactory
from stonemason.renderer.engine.rendernode import RenderNode

from .terminal import *
from .transform import *
from .composite import *


class ImageNodeFactory(RenderNodeFactory):
    def __init__(self):
        RenderNodeFactory.__init__(self)

        self._load_node('image.term.color', Color)
        self._load_node('image.term.mapnik', Mapnik_)
        self._load_node('image.term.mapnik.composer', MapnikComposer)
        self._load_node('image.term.relief.simple', SimpleRelief)
        self._load_node('image.term.relief.swiss', SwissRelief)
        self._load_node('image.term.relief.color', ColorRelief)
        self._load_node('image.term.storage.disk', DiskStorageNode)
        self._load_node('image.term.storage.s3', S3StorageNode)

        # load transform nodes
        self._load_node('image.transform.filter.min', MinFilter)

        # load composite nodes
        self._load_node('image.composite.alphablender', AlphaBlender)
        self._load_node('image.composite.imagemagick', IMComposer)

        # TODO: To be deprecated in the future release
        # load legacy names
        self._load_node('basic.color', Color)
        self._load_node('basic.blend', AlphaBlender)
        self._load_node('mapnik', Mapnik_)
        self._load_node('mapnik.composer', MapnikComposer)
        self._load_node('imagemagick', IMComposer)
        self._load_node('relief.simple', SimpleRelief)
        self._load_node('relief.swiss', SwissRelief)
        self._load_node('relief.color', ColorRelief)
        self._load_node('data.storage.disk', DiskStorageNode)
        self._load_node('data.storage.s3', S3StorageNode)

    def _load_node(self, prototype, node_class):
        assert node_class is None or issubclass(node_class, RenderNode)
        self._register[prototype] = node_class
