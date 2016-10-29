# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/28/16'

from osgeo import gdal, gdalconst
from stonemason.util.tempfn import generate_temp_filename
from stonemason.storage.concept import ObjectSerializeConcept


class RasterSerializer(ObjectSerializeConcept):
    def load(self, index, blob, metadata):
        temp_filename = '/vsimem/%s' % generate_temp_filename()
        try:
            gdal.FileFromMemBuffer(temp_filename, blob)
            source = gdal.OpenShared(temp_filename, gdalconst.GA_ReadOnly)
        except Exception as e:
            raise ValueError('RasterSerializer fails to load the object. %s' % str(e))
        finally:
            gdal.Unlink(temp_filename)

        return source

    def save(self, index, obj):
        if not obj:
            raise ValueError('RasterSerializer fails to save the object.')

        assert isinstance(obj, gdal.Dataset)

        temp_filename = '/vsimem/%s' % generate_temp_filename()

        driver = gdal.GetDriverByName('GTIFF')
        source = driver.CreateCopy(temp_filename, obj)
        del source

        try:
            statBuf = gdal.VSIStatL(temp_filename,
                                    gdal.VSI_STAT_EXISTS_FLAG |
                                    gdal.VSI_STAT_NATURE_FLAG |
                                    gdal.VSI_STAT_SIZE_FLAG)
            f = gdal.VSIFOpenL(temp_filename, 'rb')
            blob = gdal.VSIFReadL(1, statBuf.size, f)
            gdal.VSIFCloseL(f)

        finally:
            gdal.Unlink(temp_filename)

        metadata = dict()

        return blob, metadata
