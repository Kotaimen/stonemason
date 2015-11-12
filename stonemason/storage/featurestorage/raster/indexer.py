# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
from osgeo import ogr, gdalconst
from stonemason.pyramid.geo import Envelope
from stonemason.util.tempfn import generate_temp_filename
from stonemason.storage.concept import PersistentStorageConcept
from stonemason.storage.featurestorage.concept import SpatialIndexConcept, \
    InvalidFeatureIndex

SHAPEFILE_EXTENSIONS = ['.shp', '.dbf', '.prj', '.shx']


class ShpSpatialIndex(SpatialIndexConcept):
    def __init__(self, filename='index.shp'):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        source = driver.Open(filename, gdalconst.GA_ReadOnly)
        if source is None:
            raise InvalidFeatureIndex('Index file not found: %s' % filename)

        # copy to memory
        mem_driver = ogr.GetDriverByName('MEMORY')
        assert isinstance(mem_driver, ogr.Driver)
        self._index_data = mem_driver.CopyDataSource(
            source, 'index_data', ['OVERWRITE=YES'])

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

    @classmethod
    def from_persistent_storage(self, storage, index_key):
        assert isinstance(storage, PersistentStorageConcept)

        # download index shapefile and related files
        basename, _ = os.path.splitext(index_key)
        tempname = generate_temp_filename()

        try:

            for ext in SHAPEFILE_EXTENSIONS:
                with open(tempname + ext, 'wb') as fp:
                    blob, metadata = storage.retrieve(basename + ext)
                    if blob is None:
                        raise InvalidFeatureIndex(
                            '%s is missing!' % (basename + ext))
                    fp.write(bytes(blob))

            return ShpSpatialIndex(tempname + '.shp')

        finally:
            for ext in SHAPEFILE_EXTENSIONS:
                to_be_release = tempname + ext
                if os.path.exists(to_be_release):
                    os.remove(to_be_release)
