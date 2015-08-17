# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/7/15'

try:
    from .filters import MinFilter
except ImportError:
    MinFilter = None
