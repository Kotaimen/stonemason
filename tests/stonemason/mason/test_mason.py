# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/3/15'

import unittest

from stonemason.mason import Mason
from stonemason.mason import ThemeNotExist, ThemeNotLoaded, ThemeAlreadyLoaded
from stonemason.mason.theme import MemThemeManager, JsonThemeLoader
from stonemason.mason.theme import SAMPLE_THEME



class TestMason(unittest.TestCase):
    def setUp(self):
        self._manager = MemThemeManager()

        loader = JsonThemeLoader(SAMPLE_THEME)
        loader.load_into(self._manager)

        self._mason = Mason()

    def test_load_theme(self):
        theme = self._manager.get('antique')

        self._mason.load_theme(theme)
        self.assertIsNone(
            self._mason.get_tile('antique', 0, 0, 0, 1, 'png'))

        self.assertRaises(
            ThemeAlreadyLoaded, self._mason.load_theme, theme)

