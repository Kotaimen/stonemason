# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

from .imagecomposer import ImageComposer, ComposerError

try:
    from .imagemagick import ImageMagickComposer, ImageMagickError
except ImportError:
    ImageMagickComposer = None
