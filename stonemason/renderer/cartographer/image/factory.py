# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.image.factory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of factory of image render nodes.
"""

__author__ = 'ray'
__date__ = '8/14/15'

from stonemason.renderer.engine.factory import RenderNodeFactory

from .terminal import *
from .transform import *
from .composite import *


class ImageNodeFactory(RenderNodeFactory):
    """Image Node Factory

    `ImageNodeFactory` create image render nodes from their prototype name and
    parameters described in the render expression.

    Example:

        1. A terminal single color render node could be created by the following
        expression:

        .. code-block:: javascript

            "white": {
                "prototype" : "image.input.color",
                "color": "fff"
            }

        2. A filter render node could be created by the following expression:

        .. code-block:: javascript

            "filter": {
                "prototype" : "image.transform.filter.min",
                "source": "source"
                "size": "3"
            }

        3. A alpha blending node could be created by the following expression:

        .. code-block:: javascript

            "composite": {
                "prototype" : "image.composite.alphablender",
                "sources": ["source1", "source2"],
                "alpha": 0.5
            }

    Currently available nodes:

        input nodes:

            'image.input.color'
            'image.input.mapnik'
            'image.input.mapnik.composer'
            'image.input.relief.simple'
            'image.input.relief.swiss'
            'image.input.relief.color'
            'image.input.storage.disk'
            'image.input.storage.s3'

        transform nodes:

            'image.transform.filter.min'

        composite nodes:

            'image.composite.alphablender'
            'image.composite.imagemagick'


    """
    def __init__(self):
        RenderNodeFactory.__init__(self)

        self.register_node('image.input.color', Color)
        self.register_node('image.input.mapnik', Mapnik_)
        self.register_node('image.input.mapnik.composer', MapnikComposer)
        self.register_node('image.input.relief.simple', SimpleRelief)
        self.register_node('image.input.relief.swiss', SwissRelief)
        self.register_node('image.input.relief.color', ColorRelief)
        self.register_node('image.input.storage.disk', DiskStorageNode)
        self.register_node('image.input.storage.s3', S3StorageNode)

        # load transform nodes
        self.register_node('image.transform.filter.min', MinFilter)

        # load composite nodes
        self.register_node('image.composite.alphablender', AlphaBlender)
        self.register_node('image.composite.alphacomposer', AlphaComposer)
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
