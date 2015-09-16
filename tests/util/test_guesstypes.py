# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/25/15'

import unittest

from stonemason.util.guesstypes import guess_extension, guess_mimetype


class TestGuessExtension(unittest.TestCase):
    def test_guess_extension(self):
        self.assertEqual(guess_extension(None), '')
        self.assertEqual(guess_extension(''), '')
        self.assertEqual(guess_extension('application/data'), '.dat')
        self.assertEqual(guess_extension('what ever'), '')
        self.assertEqual(guess_extension('image/jpg'), '.jpg')
        self.assertEqual(guess_extension('image/jpeg'), '.jpg')
        self.assertEqual(guess_extension('image/png'), '.png')
        self.assertEqual(guess_extension('image/tiff'), '.tif')
        self.assertEqual(guess_extension('application/json'), '.json')
        self.assertEqual(guess_extension('text/xml'), '.xml')
        self.assertEqual(guess_extension('text/plain'), '.txt')


class TestGuessMimetype(unittest.TestCase):
    def test_guess_mimetype(self):
        self.assertEqual(guess_mimetype(None), 'application/data')
        self.assertEqual(guess_mimetype(''), 'application/data')
        self.assertEqual(guess_mimetype('.'), 'application/data')
        self.assertEqual(guess_mimetype('.what ever'), 'application/data')
        self.assertEqual(guess_mimetype('.dat'), 'application/data')
        self.assertEqual(guess_mimetype('.jpg'), 'image/jpeg')
        self.assertEqual(guess_mimetype('.jpeg'), 'image/jpeg')
        self.assertEqual(guess_mimetype('.tif'), 'image/tiff')
        self.assertEqual(guess_mimetype('.tiff'), 'image/tiff')


if __name__ == '__main__':
    unittest.main()
