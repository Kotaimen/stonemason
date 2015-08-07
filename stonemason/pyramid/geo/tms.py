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
    """A rectangular area on the projection surface, defined by two corner
    points ``(left, bottom, right, top)``.
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

    >>> from stonemason.pyramid import Pyramid, MetaTileIndex
    >>> from stonemason.pyramid.geo import TileMapSystem
    >>> pyramid = Pyramid(geogcs='EPSG:4326', projcs='EPSG:3857')
    >>> tms = TileMapSystem(pyramid)
    >>> tms.geogcs # doctest: +ELLIPSIS
    <osgeo.osr.SpatialReference; proxy of <Swig Object of type 'OSRSpatialReferenceShadow *' at ...> >
    >>> tms.pyramid.geogcs
    '+proj=longlat +datum=WGS84 +no_defs '
    >>> tms.forward_projection # doctest: +ELLIPSIS
    <osgeo.osr.CoordinateTransformation; proxy of <Swig Object of type 'OSRCoordinateTransformationShadow *' at ...> >
    >>> index = MetaTileIndex(4, 12, 12, 8)
    >>> tms.calc_tile_envelope(index)
    _Envelope(left=0.0, bottom=-20037508.34, right=20037508.34, top=0.0)

    .. note:: `TileMapSystem` uses `GDAL <http://www.gdal.org/>`_ for spatial
        calculations, the actual list of supported spatial references and
        coordinate transforms depends on `GDAL` installation and may vary
        between distributions.

    .. seealso:: `Geometry`_, `SpatialReference`_, `CoordinateTransformation`_

    .. _Geometry: http://gdal.org/python/osgeo.ogr.Geometry-class.html
    .. _SpatialReference: http://gdal.org/python/osgeo.osr.SpatialReference-class.html
    .. _CoordinateTransformation: http://gdal.org/python/osgeo.osr.CoordinateTransformation-class.html

    :param pyramid: The `pyramid` defines the tile map system, the following
        attributes are used to create `TileMapSystem`:

        ``Pyramid.geogcs``
            Geographic coordinate system, can be any string supported by
            :func:`~osgeo.ogr.SpatialReference.SetFromUserInput`.

        ``Pyramid.projcs``
            Projection coordinate system, can be any string supported by
            :func:`~osgeo.ogr.SpatialReference.SetFromUserInput`.
            When set to ``None``, `TileMapSystem` will try to figure
            out one from ``geogcs``.

        ``Pyramid.geogbounds``
            Boundary of the map in geography coordinate system.  Specified using
            envelope ``(min_lon, min_lat, max_lon, max_lat)``.
            The envelope is not considered as a ogr simple geometry and may
            behaviour incorrectly for some GCS if it crosses meridian line.

        ``Pyramid.projbounds``
            Boundary of the map in projection coordinate system.  Specified using
            envelope ``(left, bottom, right, top)``.  When set to ``None``,
            this will be calculated by projecting ``geogbounds`` form ``geogcs``
            to ``projcs``.  Note this calculation may fail or give a incorrect
            result due to limitations in GDAL.

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
        """Normalized pyramid object.

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
            # try figure out geogcs of the projection if its not specified
            code = self._projcs.GetAuthorityCode('geogcs')
            authority = self._projcs.GetAuthorityName('geogcs')
            if code is None or authority is None:
                raise TileMapError("Cannot figure out geogcs automaticlly.")
            self._geogcs.SetFromUserInput('%s:%s' % (authority, code))

        # XXX: Fix up wkt +over issue
        # By default PROJ.4 wraps output longitudes in the range -180 to 180.
        # The +over switch can be used to disable the default wrapping which
        # is done at a low level.
        projcs = self._projcs.ExportToProj4()
        if '+over' not in projcs.split():
            projcs += ' +over'
            self._projcs.ImportFromProj4(projcs)

        geogcs = self._geogcs.ExportToProj4()
        if '+over' not in geogcs.split():
            geogcs += ' +over'
            self._geogcs.ImportFromProj4(geogcs)

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

    def _calc_max_bbox(self):
        envelope = self.proj_bounds.GetEnvelope()
        min_x, max_x, min_y, max_y = envelope

        size_x = abs(max_x - min_x)
        size_y = abs(max_y - min_y)

        scale = max([size_x, size_y])

        # fit projection bounds to a square box, if necessary
        if size_x > size_y:
            offset_x = min_x
            offset_y = min_y - (size_x - size_y) / 2
        elif size_x < size_y:
            offset_x = min_x - (size_y - size_x) / 2
            offset_y = min_y
        else:
            offset_x = min_x
            offset_y = min_y
        return offset_x, offset_y, scale

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

        # XXX: should've cached this
        offset_x, offset_y, scale = self._calc_max_bbox()

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
