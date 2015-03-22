# -*- encoding: utf-8 -*-

"""
    stonemason.pyramid.geo.geosys
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Geographic system
"""

__author__ = 'kotaimen'
__date__ = '3/20/15'

import collections

from osgeo import osr
from osgeo import ogr

osr.UseExceptions()
ogr.UseExceptions()

from stonemason.pyramid import Pyramid
from stonemason.pyramid import TileIndex, MetaTileIndex


class TileMapError(RuntimeError):
    pass


_Envelope = collections.namedtuple('_Envelope', 'left bottom right top')


class Envelope(_Envelope):
    """A rectangular area on the projection surface, defined by two points
    ``(left, bottom, right, top)``.
    """

    @staticmethod
    def from_ogr(e):
        """Create a envelope from a call from :func:`ogr.Geometry.GetEnvelope()`,
        which is defined by ``(minx, maxx, miny, maxy)``.
        """
        return Envelope(e[0], e[2], e[1], e[3])

    def to_geometry(self, srs=None):
        """Convert the envelope to a :class:`ogr.Geometry` instance, with
        specified spatial reference system"""
        left, bottom, right, top = self
        bbox = (left, bottom, right, bottom,
                right, top, left, top, left, bottom)
        wkt = 'POLYGON((%.9f %.9f, %.9f %.9f, %.9f %.9f, %.9f %.9f, %.9f %.9f))' % bbox
        return ogr.CreateGeometryFromWkt(wkt, srs)


class TileMapSystem(object):
    """Defines geographic attributes of a `pyramid` tile map system.

    :param pyramid: The `pyramid` defines the tile map system
    :type pyramid: :class:`~stonemason.pyramid.Pyramid`
    """

    def __init__(self, pyramid):
        assert isinstance(pyramid, Pyramid)

        self._projcs = None
        self._geogcs = None
        self._forward_projection = None
        self._backward_projection = None
        self._geogbounds = None
        self._projbounds = None

        self._init_spatial_ref(pyramid)
        self._init_projections(pyramid)
        self._init_bounds(pyramid)

        # construct a normalized pyramid from calculations above
        self._pyramid = Pyramid(
            levels=pyramid.levels,
            stride=pyramid.stride,
            projcs=self._projcs.ExportToProj4(),
            geogcs=self._geogcs.ExportToProj4(),
            geogbounds=Envelope.from_ogr(self._geogbounds.GetEnvelope()),
            projbounds=Envelope.from_ogr(self._projbounds.GetEnvelope()),
        )

    @property
    def projcs(self):
        """Projection coordinate system.

        :rtype: :class:`osgeo.osr.SpatialReference`
        """
        return self._projcs

    @property
    def geogcs(self):
        """Geographic coordinate system.

        :rtype: :class:`osgeo.osr.SpatialReference`
        """
        return self._geogcs

    @property
    def forward_projection(self):
        """Defines coordinate transformation from geographic coordinate
        system to projection coordinate system.

        :rtype: :class:`osgeo.osr.CoordinateTransformation`
        """
        return self._forward_projection

    @property
    def backward_projection(self):
        """Defines coordinate transformation from projection coordinate
        system to geographic coordinate system.

        :rtype: :class:`osgeo.osr.CoordinateTransformation`
        """
        return self._backward_projection

    @property
    def geog_bounds(self):
        """Bounds of the tile map system in geometry coordinate system.

        :rtype: :class:`osgeo.osr.Geometry`
        """
        return self._geogbounds

    @property
    def proj_bounds(self):
        """Bounds of the tile map system in projection coordinate system.

        :rtype: :class:`osgeo.osr.Geometry`
        """
        return self._projbounds

    @property
    def pyramid(self):
        """Normalized pyramid in the tile map system.

        :rtype: :class:`~stonemason.pyramid.Pyramid`
        """
        return self._pyramid


    def _init_spatial_ref(self, pyramid):
        # create projection coordinate system from Pyramid
        self._projcs = osr.SpatialReference()
        self._projcs.SetFromUserInput(pyramid.projcs)
        # must be a map projection
        if not self._projcs.IsProjected():
            raise TileMapError('Not a projection coordinate system.')

        # create geographic coordinate system from Pyramid
        self._geogcs = osr.SpatialReference()
        if pyramid.geogcs is not None:
            self._geogcs.SetFromUserInput(pyramid.geogcs)
        else:
            # geogcs must matching projcs
            geogcs_attr = self._projcs.GetAttrValue('geogcs')
            self._geogcs.SetFromUserInput(geogcs_attr)

    def _init_projections(self, pyramid):
        self._forward_projection = osr.CoordinateTransformation(self._geogcs,
                                                                self._projcs)
        self._backward_projection = osr.CoordinateTransformation(self._geogcs,
                                                                 self._projcs)

    def _init_bounds(self, pyramid):
        self._geogbounds = Envelope(*pyramid.geogbounds) \
            .to_geometry(self._geogcs)
        if pyramid.projbounds is None:
            geobounds = self._geogbounds.Clone()
            geobounds.Transform(self._forward_projection)
            self._projbounds = geobounds
        else:
            self._projbounds = Envelope(*pyramid.projbounds) \
                .to_geometry(self._projcs)

    def calc_tile_envelope(self, index):
        """ Calculates envelope of given `TileIndex` of `MetaTileIndex` under
        projection coordinate system.

        :param index: Given tile index or metatile index
        :type index: :class:`~stonemason.pyramid.TileIndex` or
            :class:`~stonemason.pyramid.MetaTileIndex`

        :return: Calculated envelope
        :rtype: :class:`~stonemason.pyramid.geo.Envelope`
        """

        # just convert metatile index to higher level tile index
        if isinstance(index, MetaTileIndex):
            index = index.to_tile_index()

        assert isinstance(index, TileIndex)


        # HACK: ogr geometry returns (minx, maxx, miny, maxy) but we are
        # expecting (minx, miny, mixx, maxy)
        envelope = self.proj_bounds.GetEnvelope()
        min_x, max_x, min_y, max_y = envelope

        stride_x = abs(max_x - min_x)
        stride_y = abs(max_y - min_y)

        scale = max([stride_x, stride_y])

        # first fit projection bounds to a square box, if necessary
        if stride_x > stride_y:
            offset_x = min_x
            offset_y = min_y - (stride_x - stride_y) / 2
        elif stride_x < stride_y:
            offset_x = min_x - (stride_y - stride_x) / 2
            offset_y = min_y
        else:
            offset_x = min_x
            offset_y = min_y

        z, x, y = index.z, index.x, index.y

        norm_factor = 2. ** z

        norm_min_x = x / norm_factor
        norm_max_x = (x + 1) / norm_factor

        norm_min_y = 1 - (y + 1) / norm_factor
        norm_max_y = 1 - y / norm_factor

        envelope = Envelope(norm_min_x * scale + offset_x,
                            norm_min_y * scale + offset_y,
                            norm_max_x * scale + offset_x,
                            norm_max_y * scale + offset_y)

        return envelope


    def __repr__(self):
        return '''GeographicSystem
    projcs: %s
    geogcs: %s
    projbounds: %s
    geogbounds: %s
)''' % (self._projcs.ExportToWkt(),
        self._geogcs.ExportToWkt(),
        self._projbounds.ExportToWkt(),
        self._geogbounds.ExportToWkt())
