# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/3/15'

import unittest

from stonemason.mason import *
from stonemason.mason.theme import MemThemeManager, JsonThemeLoader
from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY, SAMPLE_THEME_NAME

from tests import skipUnlessHasGDAL


@skipUnlessHasGDAL()
class TestMason(unittest.TestCase):
    def setUp(self):
        self._manager = MemThemeManager()

        loader = JsonThemeLoader(SAMPLE_THEME_DIRECTORY, SAMPLE_THEME_NAME)
        loader.load_into(self._manager)

        self._mason = Mason()

    def test_load_theme(self):
        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)
        self._mason.load_theme(theme)

        self.assertListEqual(['sample'], self._mason.get_tile_tags())
        self.assertRaises(DuplicatedMapError, self._mason.load_theme, theme)

    def test_get_tile_tags(self):
        self.assertListEqual([], self._mason.get_tile_tags())

        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)
        self._mason.load_theme(theme)

        self.assertListEqual(['sample'], self._mason.get_tile_tags())

    def test_get_tile(self):
        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)
        self._mason.load_theme(theme)

        tile = self._mason.get_tile('sample', 0, 0, 0, 1, 'png')
        self.assertIsNotNone(tile)
