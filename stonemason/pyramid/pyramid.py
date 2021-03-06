# -*- encoding: utf-8 -*-

"""
    stonemason.pyramid.pyramid
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tile system coverage model.

"""
__author__ = 'kotaimen'
__date__ = '1/10/15'

import collections

import six

_Pyramid = collections.namedtuple('_Pyramid',
                                  '''levels stride projcs geogcs
                                  projbounds geogbounds ''')


class Pyramid(_Pyramid):
    """Quad-tree coverage model of a tile map system.

    Coordinate system parameter accepts projection string formats supported by
    `OSRSetFromUserInput`_, which includes:

        - Well known name eg: ``WGS84``
        - EPSG Code, eg: ``EPSG:3857``
        - PROJ.4 definitions, eg: ``+proj=longlat +datum=WGS84 +no_defs``

    .. note::
        `Pyramid` itself does not verify projection strings nor data bounds,
        to do that, use the constructed `Pyramid` object to create
        a :class:`~stonemason.pyramid.geo.TileMapSystem`.

    .. _OSRSetFromUserInput: http://www.gdal.org/ogr__srs__api_8h.html#a927749db01cec3af8aa5e577d032956b


    >>> from stonemason.pyramid import Pyramid
    >>> pyramid = Pyramid(levels=[4, 5, 6], stride=4)
    >>> pyramid.levels
    [4, 5, 6]
    >>> pyramid  #doctest: +ELLIPSIS
    Pyramid(levels=[4, 5, 6], stride=4, projcs='EPSG:3857', geogcs='WGS84', ... geogbounds=(-180, -85.0511, 180, 85.0511))

    :param levels: Zoom levels of the pyramid, must be a list of integers,
        default value is ``0~22``.
    :type levels: list

    :param stride: Stride of the MetaTile in this pyramid, default
        value is ``1``.
    :type stride: int

    :param projcs: Projected coordinate system used by the `Pyramid` tile map,
        default value is ``EPSG:3857``, which is a Mercator projection used by
        GoogleMaps and most web map services.
    :type projcs: str

    :param geogcs: Geographic coordinate system used by the projection, default
        value is ``WGS84``.  This value should be consistent with `projcs`.
    :type geogcs: str or None

    :param projbounds: Boundary of the map in projection coordinate system.
        Only bounding box is supported now, which is specified using a
        tuple ``(left, top, right, bottom)``.
        Default value is ``(-20037508.34,-20037508.34,20037508.34,20037508.34)``,
        which is the default coverage of GoogleMaps.
    :type projbounds: tuple or None

    :param geogbounds: Boundary of the data in geographic coordinate system.
        Specified by a tuple ``(left, top, right, bottom)``.  Default value
        is ``(-180,-85.0511,180,85.0511)``, which is the default coverage of
        GoogleMaps on ``WGS84`` datumn.
    :type projbounds: tuple
    """

    def __new__(cls,
                levels=range(0, 23),
                stride=1,
                projcs='EPSG:3857',
                geogcs='WGS84',
                projbounds= \
                        (-20037508.34, -20037508.34, 20037508.34, 20037508.34),
                geogbounds=(-180, -85.0511, 180, 85.0511)):
        levels = list(levels)
        assert isinstance(levels, list)
        assert isinstance(stride, int) and stride & (stride - 1) == 0
        assert isinstance(projcs, six.string_types)
        # geographic coordinate system is optional
        assert isinstance(geogcs, (six.string_types, None.__class__))
        # projection bounds is optional
        assert isinstance(projbounds, (tuple, list, None.__class__))
        assert isinstance(geogbounds, (tuple, list))

        return _Pyramid.__new__(cls, levels, stride, projcs, geogcs,
                                projbounds, geogbounds)

    def __repr__(self):
        # HACK: namedtuple.__repr__() returns '_Pyramid(...' on 2.7 but returns 'Pyramid(...' on 3.4 ...
        return super(Pyramid, self).__repr__().replace('_Pyramid', 'Pyramid', 1)
