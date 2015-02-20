# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/19/15'

import unittest

from stonemason.provider.formatbundle import TileFormat, InvalidTileFormat


class TestTileFormat(unittest.TestCase):
    def test_init(self):
        fmt = TileFormat(format='JPEG')
        self.assertEqual(fmt.format, 'JPEG')
        self.assertEqual(fmt.mimetype, 'image/jpeg')
        self.assertEqual(fmt.extension, '.jpg')
        self.assertEqual(fmt.parameters, {})

    def test_repr(self):
        self.assertEqual(str(TileFormat('JPEG')),
                         'TileFormat(JPEG|image/jpeg|.jpg)')

    def test_init2(self):
        fmt = TileFormat(format='JPEG', mimetype='image/jpg',
                         extension='.jpeg',
                         parameters={'quality': 80, 'optimized': True})
        self.assertEqual(fmt.format, 'JPEG')
        self.assertEqual(fmt.mimetype, 'image/jpg')
        self.assertEqual(fmt.extension, '.jpeg')
        self.assertDictEqual(fmt.parameters, {'quality': 80, 'optimized': True})

    def test_initfail(self):
        self.assertRaises(InvalidTileFormat, TileFormat, format='foobar')


if __name__ == '__main__':
    unittest.main()
