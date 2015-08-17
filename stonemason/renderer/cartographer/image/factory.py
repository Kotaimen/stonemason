# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/14/15'

from stonemason.renderer.engine.factory import RenderNodeFactory

from .terminal import *
from .transform import *
from .composite import *


class ImageNodeFactory(RenderNodeFactory):
    def __init__(self):
        RenderNodeFactory.__init__(self)

        self.register_node('image.term.color', Color)
        self.register_node('image.term.mapnik', Mapnik_)
        self.register_node('image.term.mapnik.composer', MapnikComposer)
        self.register_node('image.term.relief.simple', SimpleRelief)
        self.register_node('image.term.relief.swiss', SwissRelief)
        self.register_node('image.term.relief.color', ColorRelief)
        self.register_node('image.term.storage.disk', DiskStorageNode)
        self.register_node('image.term.storage.s3', S3StorageNode)

        # load transform nodes
        self.register_node('image.transform.filter.min', MinFilter)

        # load composite nodes
        self.register_node('image.composite.alphablender', AlphaBlender)
        self.register_node('image.composite.imagemagick', IMComposer)

        # TODO: To be deprecated in the future release
        # load legacy names
        self.register_node('basic.color', Color)
        self.register_node('basic.blend', AlphaBlender)
        self.register_node('mapnik', Mapnik_)
        self.register_node('mapnik.composer', MapnikComposer)
        self.register_node('imagemagick', IMComposer)
        self.register_node('relief.simple', SimpleRelief)
        self.register_node('relief.swiss', SwissRelief)
        self.register_node('relief.color', ColorRelief)
        self.register_node('data.storage.disk', DiskStorageNode)
        self.register_node('data.storage.s3', S3StorageNode)
