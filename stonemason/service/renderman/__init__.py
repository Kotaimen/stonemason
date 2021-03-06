# -*- encoding: utf-8 -*-

"""
    stonemason.service.renderman
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    For now, a simple multiprocessing based tile renderer.
"""

__author__ = 'kotaimen'
__date__ = '4/3/15'

from .renderman import renderman
from .script import RenderScript, RenderStats
from .walkers import create_walker, PyramidWalker, CompleteWalker, TileListWalker

