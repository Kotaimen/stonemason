# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '11/2/15'

import os
import six
from osgeo import gdal, gdalconst

from stonemason.util.tempfn import generate_temp_filename

from ..concept import ObjectSerializeConcept


class FeatureSerializeConcept(ObjectSerializeConcept):  # pragma: no cover
    pass


class RasterFeatureSerializer(FeatureSerializeConcept):
    def load(self, index, blob, metadata):
        temp_filename = generate_temp_filename()

        try:
            with open(temp_filename, 'wb') as fp:
                fp.write(blob)

            source = gdal.OpenShared(temp_filename, gdalconst.GA_ReadOnly)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        return source

    def save(self, index, obj):
        assert isinstance(obj, gdal.Dataset)

        driver = gdal.GetDriverByName('GTIFF')
        temp_filename = generate_temp_filename()

        source = driver.CreateCopy(temp_filename, obj)

        try:
            assert isinstance(source, gdal.Dataset)
            source.FlushCache()

            with open(temp_filename, 'rb') as fp:
                blob = six.b(fp.read())
            metadata = dict()

        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

            del source

        return blob, metadata
