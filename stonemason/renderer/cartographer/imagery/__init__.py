# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

IMAGERY_LAYERS = {}

from .basic import Color, Blend, Filter

IMAGERY_LAYERS[Color.PROTOTYPE] = Color

IMAGERY_LAYERS[Filter.PROTOTYPE] = Filter

IMAGERY_LAYERS[Blend.PROTOTYPE] = Blend

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
    from .imcomposer import IMComposer

    IMAGERY_LAYERS[IMComposer.PROTOTYPE] = IMComposer
    HAS_IMAGEMAGICK = True
except ImportError:
    Composer = None
    HAS_IMAGEMAGICK = False

try:
    from .shadedrelief import ShadedRelief, ColoredRelief

    IMAGERY_LAYERS[ShadedRelief.PROTOTYPE] = ShadedRelief
    IMAGERY_LAYERS[ColoredRelief.PROTOTYPE] = ColoredRelief
    HAS_SCIPY = True
except ImportError:
    ShadeRelief = None
    HAS_SCIPY = False

try:
    from .pilcomposer import PILComposer

    IMAGERY_LAYERS[PILComposer.PROTOTYPE] = PILComposer
    HAS_SCIPY = True
    HAS_SKIMAGE = True
except ImportError:
    PILComposer = None
    HAS_SCIPY = False
    HAS_SKIMAGE = False
