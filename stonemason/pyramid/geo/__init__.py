# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/20/15'

import importlib

try:
    importlib.import_module('osgeo.osr')
    importlib.import_module('osgeo.ogr')
    importlib.import_module('osgeo.gdal')

    #: A boolean indicates whether `osgeo` packages are available, if this is
    #: ``False``, then this package only contains dummy classes.
    HAS_GDAL = True
except ImportError:
    HAS_GDAL = False

if HAS_GDAL:
    from .tms import TileMapError, TileMapSystem, Envelope

else:
    class TileMapError(Exception):
        pass

    class TileMapSystem(object):
        pass

    class Envelope(object):
        pass
