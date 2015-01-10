# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/8/15'

import unittest

import stonemason.util.geo.hilbert as hilbert


class TestHibertCurve(unittest.TestCase):
    def test_xy_from_s_order0(self):
        # Order 0 Hilbert curve
        self.assertEqual(hilbert.hil_xy_from_s(0, 1), (0, 0))

    def test_xy_from_s_order1(self):
        # Order 1 Hilbert curve
        #### 0  1    x
        #### |--------|
        # 0  |  0  3  |
        # 1  |  1  2  |
        # y  |--------|
        self.assertEqual(hilbert.hil_xy_from_s(0, 1), (0, 0))
        self.assertEqual(hilbert.hil_xy_from_s(1, 1), (0, 1))
        self.assertEqual(hilbert.hil_xy_from_s(2, 1), (1, 1))
        self.assertEqual(hilbert.hil_xy_from_s(3, 1), (1, 0))

    def test_xy_from_s_order2(self):
        # Order 2 Hilbert curve
        ###### 0  1  2  3   x
        ### |--------------|
        # 0 |  0  1  14 15 |
        # 1 |  3  2  13 12 |
        # 2 |  4  7   8 11 |
        # 3 |  5  6   9 10 |
        # y |--------------|
        self.assertEqual(hilbert.hil_xy_from_s(0, 2), (0, 0))
        self.assertEqual(hilbert.hil_xy_from_s(1, 2), (1, 0))
        self.assertEqual(hilbert.hil_xy_from_s(2, 2), (1, 1))
        self.assertEqual(hilbert.hil_xy_from_s(3, 2), (0, 1))
        self.assertEqual(hilbert.hil_xy_from_s(4, 2), (0, 2))
        self.assertEqual(hilbert.hil_xy_from_s(5, 2), (0, 3))
        self.assertEqual(hilbert.hil_xy_from_s(6, 2), (1, 3))
        self.assertEqual(hilbert.hil_xy_from_s(7, 2), (1, 2))
        self.assertEqual(hilbert.hil_xy_from_s(8, 2), (2, 2))
        self.assertEqual(hilbert.hil_xy_from_s(9, 2), (2, 3))
        self.assertEqual(hilbert.hil_xy_from_s(10, 2), (3, 3))
        self.assertEqual(hilbert.hil_xy_from_s(11, 2), (3, 2))
        self.assertEqual(hilbert.hil_xy_from_s(12, 2), (3, 1))
        self.assertEqual(hilbert.hil_xy_from_s(13, 2), (2, 1))
        self.assertEqual(hilbert.hil_xy_from_s(14, 2), (2, 0))
        self.assertEqual(hilbert.hil_xy_from_s(15, 2), (3, 0))

    def test_xy_from_s_order3(self):
        # Order 3 Hilbert curve
        self.assertEqual(hilbert.hil_xy_from_s(60, 3), (6, 0))
        self.assertEqual(hilbert.hil_xy_from_s(61, 3), (6, 1))
        self.assertEqual(hilbert.hil_xy_from_s(62, 3), (7, 1))
        self.assertEqual(hilbert.hil_xy_from_s(63, 3), (7, 0))

    def test_xy_from_s_large(self):
        self.assertEqual(hilbert.hil_xy_from_s(12345678, 14),
                         (3776, 2138))

        self.assertEqual(hilbert.hil_xy_from_s(12345678, 15),
                         (2138, 3776))

        self.assertEqual(hilbert.hil_xy_from_s(12345678, 19),
                         (2138, 3776))

        self.assertEqual(hilbert.hil_xy_from_s(12345678, 20),
                         (3776, 2138))

        self.assertEqual(hilbert.hil_xy_from_s(829371542099833, 25),
                         (31152875, 17840406))

    def test_s_from_xy_order0(self):
        self.assertEqual(hilbert.hil_s_from_xy(0, 0, 1), 0)

    def test_xy_from_s_order1(self):
        order = 1
        for s in range(4 ** order):
            x, y = hilbert.hil_xy_from_s(s, order)
            self.assertEqual(hilbert.hil_s_from_xy(x, y, order), s)

    def test_xy_from_s_order2(self):
        order = 2
        for s in range(4 ** order):
            x, y = hilbert.hil_xy_from_s(s, order)
            self.assertEqual(hilbert.hil_s_from_xy(x, y, order), s)


    def test_xy_from_s_large(self):
        self.assertEqual(hilbert.hil_s_from_xy(2138, 3776, 15), 12345678)
        self.assertEqual(hilbert.hil_s_from_xy(2138, 3776, 19), 12345678)
        self.assertEqual(hilbert.hil_s_from_xy(3776, 2138, 20), 12345678)

        self.assertEqual(hilbert.hil_s_from_xy(31152875, 17840406, 25),
                         829371542099833)


if __name__ == '__main__':
    unittest.main()
