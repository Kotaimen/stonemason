# -*- encoding: utf-8 -*-

"""
    stonemason.services.renderman.walkers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Walk the render areas of a map and


"""

__author__ = 'kotaimen'
__date__ = '4/3/15'

import six
import itertools

from stonemason.pyramid import MetaTileIndex


def CompleteWalker(levels, stride):
    """Walk the complete pyramid"""

    for level in levels:
        for x in range(0, 2 ** level, stride):
            for y in range(0, 2 ** level, stride):
                yield MetaTileIndex(level, x, y, stride)


class CSVWalker(object):
    def __init__(self, tms, levels, stride):
        pass

    def __next__(self):
        raise NotImplementedError


def create_walker(tms, levels, stride, envelope, csv):
    return CompleteWalker(levels, stride)
