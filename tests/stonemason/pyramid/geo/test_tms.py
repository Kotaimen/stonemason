# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/21/15'

import unittest

from stonemason.pyramid import Pyramid, TileIndex, MetaTileIndex
from tests import HAS_GDAL, skipUnlessHasGDAL

if HAS_GDAL:
    from stonemason.pyramid.geo import TileMapSystem, Envelope


@skipUnlessHasGDAL()
class TestTileMapSystem(unittest.TestCase):
    def test_create_tms(self):
        pyramid = Pyramid(projcs='EPSG:3857',
                          geogcs='EPSG:4326',
                          geogbounds=(-180, -85.0511, 180, 85.0511),
                          projbounds=None)
        tms = TileMapSystem(pyramid)
        self.assertListEqual(tms.pyramid.levels, pyramid.levels)
        self.assertEqual(tms.pyramid.stride, pyramid.stride)
        self.assertEqual(tms.pyramid.projcs.strip(),
            "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs")
        self.assertEqual(tms.pyramid.geogcs.strip(),
            "+proj=longlat +datum=WGS84 +no_defs")
        self.assertTupleEqual(tms.pyramid.geogbounds,
                              (-180, -85.0511, 180, 85.0511))
        # XXX: It seems gdal.osr produces slight different value than
        # our original python version
        self.assertTupleEqual(tuple(map(lambda x: round(x, 2),
                                        tms.pyramid.projbounds)),
                              (-20037508.34, -20037471.21, 20037508.34,
                               20037471.21))

    def test_calc_bbox(self):
        pyramid = Pyramid(projcs='EPSG:3857',
                          geogcs='EPSG:4326',
                          geogbounds=(-180, -85.0511, 180, 85.0511),
                          projbounds=None)
        tms = TileMapSystem(pyramid)
        envelope = tms.calc_tile_envelope(TileIndex(1, 1, 1))
        self.assertTupleEqual(tuple(map(lambda x: round(x, 2),
                                        envelope)),
                              (0., -20037508.34, 20037508.34, 0.))
        envelope2 = tms.calc_tile_envelope(MetaTileIndex(4, 12, 12, 8))
        self.assertTupleEqual(envelope, envelope2)


if __name__ == '__main__':
    unittest.main()
