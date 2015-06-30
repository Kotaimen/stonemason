# -*- encoding: utf-8 -*-

"""
    stonemason.pyramid.hilbert
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Hilbert curve calculations.

    Hilbert curve algorithms are taken from (and modified):
      Henry S. Warren, Jr., Hakers's Delight Second Edition, 2012.
      Chapter 16: Hilbert's Curve

    Cython saves our headache of implement unsigned integer shifting in
    pure Python.
"""

__author__ = 'kotaimen'
__date__ = '1/9/15'

def hil_xy_from_s(unsigned long long s, int n):
    assert n < 64
    assert s < 4 ** n

    cdef int i
    cdef unsigned long long sa, sb
    cdef unsigned long long x, y, swap, cmpl
    cdef unsigned long long xp, yp

    x = 0
    y = 0

    for i in range(0, 2 * n, 2):
        sa = (s >> (i + 1)) & 1
        sb = (s >> i) & 1

        swap = (sa ^ sb) - 1
        cmpl = -(sa & sb)
        x = x ^ y
        y = y ^ (x & swap) ^ cmpl
        x = x ^ y

        x = (x >> 1) | (sa << 63)
        y = (y >> 1) | ((sa ^ sb) << 63)

    xp = x >> (64 - n)
    yp = y >> (64 - n)

    return xp, yp

def hil_s_from_xy(unsigned long long x, unsigned long long y, int n):
    assert n < 64

    cdef int i, xi, yi
    cdef unsigned long long s

    s = 0
    for i in range(n - 1, -1, -1):
        xi = (x >> i) & 1
        yi = (y >> i) & 1
        s = 4 * s + 2 * xi + (xi ^ yi)

        x = x ^ y
        y = y ^ (x & (yi - 1))
        x = x ^ y

        x = x ^ (-xi & (yi - 1))
        y = y ^ (-xi & (yi - 1))

    return s

