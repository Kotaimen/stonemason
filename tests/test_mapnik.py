# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/9/15'

import unittest

from tests import skipUnlessHasMapnik, mapnik


@skipUnlessHasMapnik()
class TestMapnik(unittest.TestCase):
    def test_mapnik_version(self):
        self.assertGreaterEqual(mapnik.mapnik_version(), 200300)


if __name__ == '__main__':
    unittest.main()
