# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/8/15'

"""
    stonemason.util.geo.hilbert
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Hilbert curve calculations.

"""

# XXX: This is implemented cython for unsigned integer bit operation
from . import _hilbert


def hil_xy_from_s(s, n):
    """ Compute coordinate from given Hilbert curve length.

    :param s: Length of the Hilbert curve.
    :param n: Order of the Hilbert curve
    :return: Coordinate as a tuple (x, y).
    :returns: tuple
    """
    assert n < 64
    assert s < 4 ** n
    return _hilbert.hil_xy_from_s(s, n)


def hil_s_from_xy(x, y, n):
    """ Compute Hilbert curve length from given coordinate

    Given the "order" n of a Hilbert curve and coordinates x and y,
    computes the length s of the curve from the origin to (x, y).

    :param x: x coordinate.
    :param y: y coordinate.
    :param n: Order of the Hilbert curve
    :return: Hilbert curve length
    :returns: int
    """
    assert n < 64
    return _hilbert.hil_s_from_xy(x, y, n)
