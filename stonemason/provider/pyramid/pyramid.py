# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/10/15'

"""
    stonemason.provider.pyramid.pyramid
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The Quad Tree tile system, with optional CRS&Boundary check.

"""

import collections


_Pyramid = collections.namedtuple('_Pyramid', '''levels crs proj boundary''')


class Pyramid(_Pyramid):
    """Quad-tree grid system of a `tile` map.

    """

    pass

