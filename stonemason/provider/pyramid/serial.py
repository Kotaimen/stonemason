# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/10/15'

"""
    stonemason.provider.pyramid.serial
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Convert tile index to a serial number
"""

import math

import stonemason.util.geo.hilbert as hilbert


class Hilbert(object):
    @staticmethod
    def coord2serial(z, x, y):
        """ Convert tile coordinate to a unique serial

        The serial is a 64bit integer, each tile has a unique, ordered serial,
        higher scale zoom level tiles always has a smaller serial.
        """
        assert 0 <= z <= 28

        return (z << 58) | hilbert.hil_s_from_xy(x, y, z)

    @staticmethod
    def coord2dir(z, x, y):
        """ Return a directory name for a given tile coordinate.

        Each directory contains 4096 tiles or 256 subdirs.
        """
        assert 0 <= z <= 28

        dirs = ['%02d' % z, ]

        # zoom level has more than 4096 tiles
        if z > 6:
            # Group by Hilbert length as 64x64 blocks
            block = hilbert.hil_s_from_xy(x, y, z) // 4096

            # Max number of hex digits for the block
            digits = (z - 5) // 2

            # Hex string zero padding to even length
            hex_str = ('%X' % block).zfill(digits % 2 + digits)

            dirs.extend(hex_str[i:i + 2] for i in range(0,len(hex_str), 2))

        return dirs


class Legacy(object):
    """ Legacy serial used in Mason and older Pathologist systems.

    Copied code, works fine but is not cool anymore (besides stupid and slow).
    """

    @staticmethod
    def coord2serial(z, x, y):
        """ Convert tile coordinate to an integer serial

        Flatten tile coordinate (z, x, y) to a serial by::

            (4^(z)-1) / 3 + 2^z * y + x

        This formula is calculated form total number of tiles of layer 0~k::

            Sum[4^n, {n, 0, k}] = (4^(k+1)-1) / 3


        For a 32 bit integer serial, the largest supported tile layer is 15.
        For a 64 bit integer serial, the largest supported tile layer is 31.
        """

        # Limit serial to 64 bit signed integer
        assert z >= 0 and z <= 31
        # Number of tile per axis
        dim = 2 ** z
        assert x < dim and x >= 0 and y < dim and y >= 0

        return (4 ** z - 1) // 3 + y * dim + x

    @staticmethod
    def coord2dir(z, x, y):

        """ Return a directory name list for a given tile coordinate

        Groups adjacent m*m tiles in a sub directory to improve file system
        performance.  Returns a list of directory names, to create a
        directory str, use os.path.join(*list)
        """

        assert 0 <= z <= 31
        dim = 2 ** z
        assert 0 <= x < dim and 0 <= y < dim

        # Group 4096 tiles
        m = 64

        zdiff = int(math.floor(math.log(m) / math.log(2)))

        # layer has less than m*m tiles, just use z as pathname
        if z <= zdiff:
            return ['%02d' % z, ]

        # metatile number
        mx, my = x // m, y // m
        mz = z - zdiff
        mn = 2 ** mz * my + mx

        # calculate how many digits are needed
        digits = len('%x' % (4 ** mz - 1))
        if digits % 2 != 0:
            digits += 1
        hex_str = ('%%0%dX' % digits) % mn

        # split hex string into 2 char tuple
        dirs = list((hex_str[i:i + 2] for i in range(0, len(hex_str), 2)))
        dirs.insert(0, '%02d' % z)

        return dirs
