# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

try:
    from .color import Color
except ImportError:
    Color = None

try:
    from .mapnik_ import Mapnik_, MapnikComposer
except ImportError:
    Mapnik_ = None
    MapnikComposer = None

try:
    from .relief import SimpleRelief, SwissRelief, ColorRelief
except ImportError:
    SimpleRelief = None
    SwissRelief = None
    ColorRelief = None

try:
    from .storage import DiskStorageNode, S3StorageNode
except ImportError:
    DiskStorageNode = None
    S3StorageNode = None
