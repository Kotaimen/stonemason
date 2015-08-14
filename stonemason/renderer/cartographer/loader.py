# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/14/15'

from stonemason.renderer.expression import ImageNodeFactory

from .image import *


def register_image_render_node(factory):
    assert isinstance(factory, ImageNodeFactory)

    # load terminal nodes
    factory.load_node('image.term.color', Color)
    factory.load_node('image.term.mapnik', Mapnik_)
    factory.load_node('image.term.mapnik.composer', MapnikComposer)
    factory.load_node('image.term.relief.simple', SimpleRelief)
    factory.load_node('image.term.relief.swiss', SwissRelief)
    factory.load_node('image.term.relief.color', ColorRelief)
    factory.load_node('image.term.storage.disk', DiskStorageNode)
    factory.load_node('image.term.storage.s3', S3StorageNode)

    # load transform nodes
    factory.load_node('image.transform.filter.min', MinFilter)

    # load composite nodes
    factory.load_node('image.composite.alphablender', AlphaBlender)
    factory.load_node('image.composite.imagemagick', IMComposer)

    # TODO: To be deprecated in the future release
    # load legacy names
    factory.load_node('basic.color', Color)
    factory.load_node('basic.blend', AlphaBlender)
    factory.load_node('mapnik', Mapnik_)
    factory.load_node('mapnik.composer', MapnikComposer)
    factory.load_node('imagemagick', IMComposer)
    factory.load_node('relief.simple', SimpleRelief)
    factory.load_node('relief.swiss', SwissRelief)
    factory.load_node('relief.color', ColorRelief)
    factory.load_node('data.storage.disk', DiskStorageNode)
    factory.load_node('data.storage.s3', S3StorageNode)
