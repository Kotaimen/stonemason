# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

IMAGERY_LAYERS = {}

try:
    from .mapnik_ import Mapnik_, MapnikComposer

    IMAGERY_LAYERS[Mapnik_.PROTOTYPE] = Mapnik_
    IMAGERY_LAYERS[MapnikComposer.PROTOTYPE] = MapnikComposer
    HAS_MAPNIK = True
except ImportError:
    Mapnik_ = None
    MapnikComposer = None
    HAS_MAPNIK = False

try:
    from .composer import Composer

    IMAGERY_LAYERS[Composer.PROTOTYPE] = Composer
    HAS_IMAGEMAGICK = True
except ImportError:
    Composer = None
    HAS_IMAGEMAGICK = False

try:
    from .shaderelief import ShadeRelief

    IMAGERY_LAYERS[ShadeRelief.PROTOTYPE] = ShadeRelief
    HAS_SCIPY = True
except ImportError:
    ShadeRelief = None
    HAS_SCIPY = False

from .pilcarto import PILColor, PILInvert, PILBlend, PILComposer

IMAGERY_LAYERS[PILColor.PROTOTYPE] = PILColor

IMAGERY_LAYERS[PILInvert.PROTOTYPE] = PILInvert

IMAGERY_LAYERS[PILBlend.PROTOTYPE] = PILBlend

IMAGERY_LAYERS[PILComposer.PROTOTYPE] = PILComposer

