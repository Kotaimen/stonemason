# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'


try:
    from .alphacomposer import AlphaComposer
except ImportError:
    AlphaComposer = None

try:
    from .imblender import IMComposer
except ImportError:
    IMComposer = None
