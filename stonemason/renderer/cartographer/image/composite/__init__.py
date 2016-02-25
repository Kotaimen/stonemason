# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

try:
    from .alphablender import AlphaBlender
except ImportError:
    AlphaBlender = None

try:
    from .alphablender import AlphaComposer
except ImportError:
    AlphaComposer = None

try:
    from .imblender import IMComposer
except ImportError:
    IMComposer = None
