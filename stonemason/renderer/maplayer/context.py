# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/19/15'

from collections import namedtuple


_Foo = namedtuple(
    'LayerContext',
    'pyramid target_bbox target_size')


class MapContext(_Foo):
    """

    :param pyramid: The target space reference system.

    :param target_bbox: The target render area.

    :param target_size: The pixel size of the target bounding box.

    :param target_scale: The target_scale indicates the ratio between map
                         distance and ground distance.

    :param target_resolution: The target_resolution indicates the distance on
                              the ground that represented by a single pixel.
                              For example, ``78271.5170`` meters/pixel.

    """

    def __new__(cls, pyramid=None, target_bbox=None, target_size=None):
        return _Foo.__new__(
            cls, pyramid=pyramid, target_bbox=target_bbox,
            target_size=target_size)

