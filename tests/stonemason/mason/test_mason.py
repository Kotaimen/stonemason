# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/3/15'

import unittest

from stonemason.mason import Mason
from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY, SAMPLE_THEME


class TestMason(unittest.TestCase):
    def setUp(self):
        self._mason = Mason()

    def tearDown(self):
        self._mason.close()

    def test_load_theme_from_file(self):
        self._mason.load_theme_from_file(SAMPLE_THEME)
        self.assertIsNone(
            self._mason.get_tile('antique', 0, 0, 0, 1, 'png'))

    def test_load_theme_from_directory(self):
        self._mason.load_theme_from_directory(SAMPLE_THEME_DIRECTORY)
        self.assertIsNone(
            self._mason.get_tile('antique', 0, 0, 0, 1, 'png'))

    def test_get_theme(self):
        self._mason.load_theme_from_file(SAMPLE_THEME)

        expected = {
            "pyramid": {
                "levels": range(0, 23),
                "stride": 1,
                "crs": "EPSG:4326",
                "proj": "EPSG:3857",
                "boundary": (-180, -85.0511, 180, 85.0511)
            },
            "tag": "nanook",
            "metadata": {
                "attribution": "I am a sample."
            }
        }

        m = self._mason.get_theme('antique')

        self.assertEqual('antique', m['tag'])
        self.assertEqual('K&R', m['metadata']['attribution'])
