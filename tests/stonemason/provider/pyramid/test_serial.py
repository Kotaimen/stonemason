# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/10/15'

import unittest

import stonemason.provider.pyramid.serial as serial


class TestHilbert(unittest.TestCase):
    def test_serial(self):
        self.assertEqual(serial.Hilbert.coord2serial(0, 0, 0), 0)
        self.assertEqual(serial.Hilbert.coord2serial(1, 0, 0),
                         0x400000000000000)
        self.assertEqual(serial.Hilbert.coord2serial(3, 4, 5),
                         0xc00000000000023)
        self.assertEqual(serial.Hilbert.coord2serial(8, 8, 8),
                         0x2000000000000080)
        self.assertEqual(serial.Hilbert.coord2serial(28, 134217727, 134217728),
                         0x707fffffffffffff)

    def test_cood(self):
        self.assertListEqual(serial.Hilbert.coord2dir(0, 0, 0), ['00'])
        self.assertListEqual(serial.Hilbert.coord2dir(3, 4, 5), ['03'])
        self.assertListEqual(serial.Hilbert.coord2dir(7, 1, 1), ['07', '00'])
        self.assertListEqual(serial.Hilbert.coord2dir(7, 64, 1), ['07', '03'])
        self.assertListEqual(serial.Hilbert.coord2dir(19, 468432, 187688),
                             ['19', '03', '1F', '7C', '85'])
        self.assertListEqual(serial.Hilbert.coord2dir(20, 1000, 2000),
                             ['20', '00', '00', '03', '00'])


class TestLegacy(unittest.TestCase):
    def test_serial(self):
        self.assertEqual(serial.Legacy.coord2serial(0, 0, 0), 0)
        self.assertEqual(serial.Legacy.coord2serial(1, 0, 0), 1)
        self.assertEqual(serial.Legacy.coord2serial(3, 4, 5), 65)
        self.assertEqual(serial.Legacy.coord2serial(8, 8, 8), 23901)
        self.assertEqual(serial.Legacy.coord2serial(29, 0, 0),
                         96076792050570581)

    def test_coord(self):
        self.assertListEqual(serial.Legacy.coord2dir(0, 0, 0), ['00'])
        self.assertListEqual(serial.Legacy.coord2dir(7, 1, 1), ['07', '00'])
        self.assertListEqual(serial.Legacy.coord2dir(7, 64, 1), ['07', '01'])
        self.assertListEqual(serial.Legacy.coord2dir(19, 468432, 187688),
                             ['19', '01', '6E', '9C', '97'])
        self.assertListEqual(serial.Legacy.coord2dir(20, 1000, 2000),
                             ['20', '00', '07', 'C0', '0F'])


if __name__ == '__main__':
    unittest.main()
