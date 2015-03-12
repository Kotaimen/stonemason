# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/11/15'

import unittest
from distutils.version import LooseVersion

try:
    from osgeo import osr
    from osgeo import ogr
    from osgeo import gdal

    osr.UseExceptions()
    ogr.UseExceptions()
    gdal.UseExceptions()
except ImportError:
    pass

from tests import skipUnlessHasGDAL


@skipUnlessHasGDAL()
class TestGDAL(unittest.TestCase):
    def test_gdal_verison(self):
        self.assertGreaterEqual(LooseVersion(gdal.__version__),
                                LooseVersion('1.10.0'))

    def test_ogr(self):
        geom = ogr.Geometry(wkt='POINT(0 0)')
        self.assertEqual(geom.GetGeometryType(), 1)
        self.assertEqual(geom.Buffer(1).GetGeometryType(), 3)

    def test_osr(self):
        crs1 = osr.SpatialReference()
        crs1.SetFromUserInput('WGS84')
        crs2 = osr.SpatialReference()
        crs2.SetFromUserInput('EPSG:3857')

        transform = osr.CoordinateTransformation(crs1, crs2)

        point = transform.TransformPoint(180, 0)
        self.assertAlmostEqual(point[0], 20037508.342789248)
        self.assertAlmostEqual(point[1], 0.)


if __name__ == '__main__':
    unittest.main()
