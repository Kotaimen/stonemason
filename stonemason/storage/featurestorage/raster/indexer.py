# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
from osgeo import osr, ogr, gdalconst
from stonemason.pyramid.geo import Envelope
from stonemason.util.tempfn import generate_temp_filename
from stonemason.storage.concept import PersistentStorageConcept
from ..concept import SpatialIndexConcept
from ..errors import InvalidFeatureIndex


class ShpSpatialIndex(SpatialIndexConcept):
    SHAPEFILE_EXTS = ['.shp', '.dbf', '.prj', '.shx']

    def __init__(self, storage, shapefile='index.shp'):
        assert isinstance(storage, PersistentStorageConcept)
        self._storage = storage

        # download index shapefile and related files
        basename, _ = os.path.splitext(shapefile)
        basename_local = generate_temp_filename()
        for ext in self.SHAPEFILE_EXTS:
            with open(basename_local + ext, 'wb') as fp:
                blob, metadata = self._storage.retrieve(basename + ext)
                if blob is None:
                    raise InvalidFeatureIndex(
                        '%s is missing!' % (basename + ext))
                fp.write(blob)

        # open the shapefile
        driver = ogr.GetDriverByName('ESRI Shapefile')
        source = driver.Open(basename_local + '.shp', gdalconst.GA_ReadOnly)
        if source is None:
            raise InvalidFeatureIndex('Index file not found: %s' % shapefile)
        index = source.GetLayer(0)
        if index is None:
            raise InvalidFeatureIndex('Index layer not found!')

        # set root prefix
        self._prefix = os.path.split(shapefile)[0]

        # resources need to be release
        self._source = source
        self._index = index
        self._basename_local = basename_local

    @property
    def crs(self):
        return self._index.GetSpatialRef()

    @property
    def envelope(self):
        minx, maxx, miny, maxy = self._index.GetExtent()
        return minx, miny, maxx, maxy

    def intersection(self, envelope, crs='EPSG:4326'):
        target_crs = osr.SpatialReference()
        target_crs.SetFromUserInput(crs)

        target_geom = Envelope(*envelope).to_geometry(srs=target_crs)
        if not target_crs.IsSame(self.crs):
            target_geom.TransformTo(self.crs)

        self._index.SetSpatialFilter(target_geom)

        result = list()
        for feature in self._index:
            location = feature.GetField('location')
            if not location:
                continue

            location = os.path.normpath(os.path.join(self._prefix, location))
            result.append(location)

        return result

    def close(self):
        self._index = None
        self._source = None

        for ext in self.SHAPEFILE_EXTS:
            filename = os.path.join(self._basename_local, ext)
            if os.path.exists(filename):
                os.remove(filename)
