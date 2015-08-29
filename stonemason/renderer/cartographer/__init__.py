# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of back-ends of renderer.
"""

__author__ = 'ray'
__date__ = '4/20/15'

from .image import ImageNodeFactory, ImageFeature
from .inspect import has_module, has_executable, HAS_GDAL, HAS_IMAGEMAGICK, \
    HAS_SCIPY, HAS_SKIMAGE, HAS_MAPNIK
