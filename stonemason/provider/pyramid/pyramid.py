# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/10/15'

"""
    stonemason.provider.pyramid.pyramid
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The Quad Tree tile system, with optional CRS&Boundary check.

"""

import collections
import re

import six

_Pyramid = collections.namedtuple('_Pyramid',
                                  '''levels stride crs proj boundary''')


class Pyramid(_Pyramid):
    """Quad-tree grid system of a `tile` map.

    **Projection**

    `crs` and `proj` accepts projection string formats supported by
    `OSRSetFromUserInput`_, which includes:

     - Well known name eg: ``WGS84``
     - EPSG Code, eg: ``EPSG:3857``
     - PROJ.4 definitions, eg: ``+proj=longlat +datum=WGS84 +no_defs``

    Note `Pyramid` does not verify projection strings.


    .. warning:: Attributes of Pyramid is subject to change before design
        stabilizes.

    .. _OSRSetFromUserInput: http://www.gdal.org/ogr__srs__api_8h.html#a927749db01cec3af8aa5e577d032956b


    >>> from stonemason.provider.pyramid import Pyramid
    >>> pyramid = Pyramid(levels=[4,5,6],stride=4)
    >>> pyramid.levels
    [4, 5, 6]
    >>> pyramid
    Pyramid(levels=[4, 5, 6], stride=4, crs='EPSG:4326', proj='EPSG:3857', boundary=(-180, -85.0511, 180, 85.0511))

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0-22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int

    :param crs: Coordinate Reference System (Geographic Coordinate System)
        of the map data.  default value is ``EPSG:4326``, which is the common
        WGS84 datum.
    :type crs: str

    :param proj: Projected coordinate system of the map, default value
        is ``EPSG:3857``, which is Mercator projection used by GoogleMaps
        and most web map services.

    :type proj: str

    :param boundary: Boundary of the map specified in data `crs`.
        Map boundary in specified `crs`, only simple bounding box is supported
        as of now, in the form of ``(left, top, right, bottom)``.
        Default value is ``(-180,-85.0511,180,85.0511)``, which is the default
        coverage of Google Maps
    """

    def __new__(cls,
                levels=range(0, 23),
                stride=1,
                crs='EPSG:4326',
                proj='EPSG:3857',
                boundary=(-180, -85.0511, 180, 85.0511)):

        levels = list(levels)
        assert isinstance(levels, list)
        assert isinstance(stride, int) and stride & ( stride - 1 ) == 0
        assert isinstance(boundary, (tuple, list)) and len(boundary) == 4
        assert isinstance(crs, six.string_types)
        assert isinstance(proj, six.string_types)

        return _Pyramid.__new__(cls, levels, stride, crs, proj, boundary)

    def __repr__(self):
        # HACK: namedtuple.__repr__() returns '_Pyramid(...' on 2.7 but returns 'Pyramid(...' on 3.4 ...
        return super(Pyramid, self).__repr__().replace('_Pyramid', 'Pyramid', 1)
