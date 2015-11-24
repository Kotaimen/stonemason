# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import six
from osgeo import gdal, ogr, gdalconst
from stonemason.pyramid.geo import Envelope
from stonemason.util.tempfn import generate_temp_filename
from stonemason.storage.concept import PersistentStorageConcept
from stonemason.storage.featurestorage.concept import SpatialIndexConcept, \
    InvalidFeatureIndex

SHAPEFILE_EXTENSIONS = ['.shp', '.dbf', '.prj', '.shx']


class ShpSpatialIndex(SpatialIndexConcept):
    def __init__(self, shp, dbf, prj, shx):
        self._tempname = generate_temp_filename()
        gdal.FileFromMemBuffer('/vsimem/%s.shp' % self._tempname, shp.read())
        gdal.FileFromMemBuffer('/vsimem/%s.dbf' % self._tempname, dbf.read())
        gdal.FileFromMemBuffer('/vsimem/%s.prj' % self._tempname, prj.read())
        gdal.FileFromMemBuffer('/vsimem/%s.shx' % self._tempname, shx.read())

        driver = ogr.GetDriverByName('ESRI Shapefile')
        assert driver is not None

        self._index_data = driver.Open(
            '/vsimem/%s.shp' % self._tempname, gdalconst.GA_Update)

        self._index = self._index_data.GetLayer(0)
        if self._index is None:
            raise InvalidFeatureIndex('Index layer not found!')

    @property
    def crs(self):
        return self._index.GetSpatialRef()

    @property
    def envelope(self):
        minx, maxx, miny, maxy = self._index.GetExtent()
        return minx, miny, maxx, maxy

    def intersection(self, envelope):
        query_crs = self._index.GetSpatialRef()
        query_geom = Envelope(*envelope).to_geometry(srs=query_crs)

        self._index.SetSpatialFilter(query_geom)

        result = list()
        for feature in self._index:
            location = feature.GetField('location')
            if not location:
                continue
            result.append(location)

        return result

    def close(self):
        self._index = None
        self._source = None

        for ext in SHAPEFILE_EXTENSIONS:
            gdal.Unlink('/vsimem/%s%s' % (self._tempname, ext))

    @classmethod
    def from_persistent_storage(self, storage, index_key):
        assert isinstance(storage, PersistentStorageConcept)

        def _get_buffer(basename, ext):
            key = basename + ext
            blob, metadata = storage.retrieve(key)
            if blob is None:
                raise InvalidFeatureIndex(
                    'Failed to get shapefile index "%s!"' % key)
            return blob

        basename, _ = os.path.splitext(index_key)

        # download index shapefile and related files
        shp = six.BytesIO(_get_buffer(basename, '.shp'))
        dbf = six.BytesIO(_get_buffer(basename, '.dbf'))
        prj = six.BytesIO(_get_buffer(basename, '.prj'))
        shx = six.BytesIO(_get_buffer(basename, '.shx'))

        return ShpSpatialIndex(shp, dbf, prj, shx)
