# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/21/15'

IMAGERY_LAYERS = {}

from .basic import Color, Blend, MedianPILFilter, MinPILFilter, MaxPILFilter, \
    GaussianBlurPILFilter, UnsharpMaskPILFilter, GammaAdjustment

IMAGERY_LAYERS[Color.PROTOTYPE] = Color
IMAGERY_LAYERS[MedianPILFilter.PROTOTYPE] = MedianPILFilter
IMAGERY_LAYERS[MinPILFilter.PROTOTYPE] = MinPILFilter
IMAGERY_LAYERS[MaxPILFilter.PROTOTYPE] = MaxPILFilter
IMAGERY_LAYERS[GaussianBlurPILFilter.PROTOTYPE] = GaussianBlurPILFilter
IMAGERY_LAYERS[UnsharpMaskPILFilter.PROTOTYPE] = UnsharpMaskPILFilter
IMAGERY_LAYERS[GammaAdjustment.PROTOTYPE] = GammaAdjustment
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
    from .shadedrelief import SimpleRelief, SwissRelief, ColorRelief

    IMAGERY_LAYERS[SimpleRelief.PROTOTYPE] = SimpleRelief
    IMAGERY_LAYERS[SwissRelief.PROTOTYPE] = SwissRelief
    IMAGERY_LAYERS[ColorRelief.PROTOTYPE] = ColorRelief
    HAS_SCIPY = True
except ImportError:
    SimpleRelief = None
    SwissRelief = None
    ColorRelief = None
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

try:
    from .storage import DiskStorageLayer, S3StorageLayer

    IMAGERY_LAYERS[DiskStorageLayer.PROTOTYPE] = DiskStorageLayer
    IMAGERY_LAYERS[S3StorageLayer.PROTOTYPE] = S3StorageLayer

except ImportError:
    DiskStorageLayer = None
    S3StorageLayer = None
