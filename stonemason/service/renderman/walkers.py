# -*- encoding: utf-8 -*-

"""
    stonemason.services.renderman.walkers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Walk the render areas of a map and


"""

__author__ = 'kotaimen'
__date__ = '4/3/15'

import six
from six.moves import xrange
import csv
import itertools

from stonemason.pyramid import MetaTileIndex
from stonemason.pyramid.geo import TileMapSystem

from .script import RenderScript


class PyramidWalker(object):
    """Walk through the pyramid and generate
    :class:`~stonemason.pyramid.MetaTileIndex` to render."""

    def __iter__(self):
        raise StopIteration


class CompleteWalker(object):
    """Walk the complete pyramid."""

    def __init__(self, levels, stride):
        self.levels = levels
        self.stride = stride

    def __iter__(self):
        for level in self.levels:
            for x in xrange(0, 2 ** level, self.stride):
                for y in xrange(0, 2 ** level, self.stride):
                    yield MetaTileIndex(level, x, y, self.stride)


class TileListWalker(object):
    """Walked given tile list in a CSV file."""

    def __init__(self, levels, stride, csv_file):
        self.levels = levels
        self.stride = stride
        self.csv_file = csv_file

    def __iter__(self):
        sdiff = len(bin(self.stride)) - 3
        with open(self.csv_file, 'rb') as fp:
            reader = csv.reader(fp)
            for row in reader:
                tz, tx, ty = tuple(map(int, row))
                for z in self.levels:
                    zdiff = z - tz
                    if zdiff < sdiff:
                        # skip this level if its smaller than min allowed layer
                        continue
                    dim = 2 ** zdiff
                    for x in xrange(tx * dim, (tx + 1) * dim, self.stride):
                        for y in xrange(ty * dim, (ty + 1) * dim, self.stride):
                            yield MetaTileIndex(z, x, y, self.stride)


def create_walker(script, tms):
    """ Create a walker in one of the three modes:

    `Complete`
        Render the entire Pyramid, enabled when both `envelope` and
        `csv_file` parameter is ``None``.

    `Envelope`
        Render the MetaTiles intersects with given Envelope,
        enabled when `envelope` parameter is given and  `csv_file`
        parameter is ``None``.

    `Predefined List`
        Render MetaTiles in a given file, which is a CSV file
        containing three columns defines tile index coordinate
        ``z, x, y``.  A row in the file means a :class:`~stonemason.pyramid.Tile`,
        with given :class:`~stonemason.pyramid.TileIndex` needs rendering.

    :param script: Render job control.
    :type script: :class:`~stonemason.services.renderman.RenderScript`

    :param tms: The `TileMapSystem` of rendering theme.
    :type tms: :class:`~stonemason.pyramid.geo.TileMapSystem`

    :return: Created walker
    :rtype: :class:`~stonemason.services.renderman.PyramidWalker`
    """
    assert isinstance(script, RenderScript)
    assert isinstance(tms, TileMapSystem)
    if script.levels is None:
        script = script._replace(levels=tms.pyramid.levels)

    if script.csv_file:
        return TileListWalker(tms.pyramid.levels, tms.pyramid.stride,
                              script.csv_file)
    elif script.envelope:
        raise NotImplementedError
    else:
        return CompleteWalker(tms.pyramid.levels, tms.pyramid.stride)
