# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

IMAGERY_LAYERS = {}

try:
    from .mapnik_ import Mapnik_

    IMAGERY_LAYERS[Mapnik_.PROTOTYPE] = Mapnik_
    HAS_MAPNIK = True
except ImportError:
    Mapnik_ = None
    HAS_MAPNIK = False

try:
    from .composer import Composer

    IMAGERY_LAYERS[Composer.PROTOTYPE] = Composer
    HAS_IMAGEMAGICK = True
except ImportError:
    Composer = None
    HAS_IMAGEMAGICK = False

from .imagery import Black, Invert, AlphaBlend

IMAGERY_LAYERS[Black.PROTOTYPE] = Black

IMAGERY_LAYERS[Invert.PROTOTYPE] = Invert

IMAGERY_LAYERS[AlphaBlend.PROTOTYPE] = AlphaBlend



