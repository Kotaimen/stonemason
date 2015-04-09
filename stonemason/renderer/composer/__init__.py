# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

from .imagecomposer import ImageComposer, ComposerError

try:
    from .imagemagick import ImageMagickComposer, ImageMagickError
    #: A boolean indicates whether ImageMagick image processing utility
    #: is available.
    HAS_IMAGEMAGICK = True
except ImportError:
    HAS_IMAGEMAGICK = False

    class ImageMagickComposer:
        pass

    class ImageMagickError:
        pass