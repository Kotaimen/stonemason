# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/5/15'

try:
    from .mapnik_ import MapnikRenderer
except ImportError:
    MapnikRenderer = None
