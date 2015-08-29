# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.engine.context
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The context that defines what, where and how to render.
"""

__author__ = 'ray'
__date__ = '4/20/15'

from collections import namedtuple

_RenderContext = namedtuple(
    'RenderContext',
    '''map_proj map_bbox map_size scale_factor meta_index''')


class RenderContext(_RenderContext):
    """Defines rendering parameters and cartographer contexts. Concepts
    are explained here:

    Map Projection
        Projection used by this map.

    Map Bounding Box
        Rectangular area to render on the map, in map projection coordinate
        system units (usually meters or degrees).

    PPI
        Number of pixels per inch, default value is 90.7, which is
        calculated from "standardized rendering pixel size".

        .. math::

            0.28mm = 0.011023622inch ~= 90.7PPI

    Pixel Size
        Map width and height specified in pixels.

    Map Size
        Physical size of the map, calculated from pixel size and PPI.

    Scale Denominator
        Controls level of details shown on the map, calculated from

        .. math::

            denominator = map\_bounding\_box\_width / map\_size

    Pixel Aspect Ratio
        If the aspect ratio of map bounding box and map size differs, then the
        pixel is not square, currently unsupported.

    Scale Factor
        Scales PPI when rasterilze a map feature, essentially multiplies
        resolution, useful when rendering maps for high resolution devices.

    Resolution

        .. math::

            resolution = scale\_factor * PPI


    :param map_proj: The coordinate reference system of the target map. Projection
        string accepted by :py:meth:`osgeo.osr.SpatialReference.SetFromUserInput`.
    :type map_proj: str

    :param map_bbox: Map bounding box on projection coordinate system,
        as ``(left, bottom, right, top)``, defines map area to render.
    :type map_bbox: tuple

    :param map_size: Pixel size of the rendered map as ``(width, height)``.
        Note when aspect ratio other than ``1`` is not supported.
        Eg: mapnik will try to auto fix aspect ratio
        by resize `map_bbox`.
    :type map_size: tuple

    :param scale_factor: Multiply the map resolution by given `scale_factor`,
        a value great than ``1`` increases resolution, where a value smaller
        than ``1`` decreases resolution.  Default value is ``1``.
    :type scale_factor: float

    :param meta_index: Special index for retrieve data from metatile storage
        renderer node.
    :type meta_index: :class:`~stonemason.pyramid.MetaTileIndex`

    .. seealso::

        `Documentation for OGRSpatialReference::SetFromUserInput <http://www.gdal.org/classOGRSpatialReference.html#aec3c6a49533fe457ddc763d699ff8796>`_


    """

    def __new__(cls, map_proj=None, map_bbox=None, map_size=None,
                scale_factor=1, meta_index=None):
        return _RenderContext.__new__(cls,
                                      map_proj=map_proj,
                                      map_bbox=map_bbox,
                                      map_size=map_size,
                                      scale_factor=scale_factor,
                                      meta_index=meta_index)
