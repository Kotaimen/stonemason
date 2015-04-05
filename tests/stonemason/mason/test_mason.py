# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/3/15'

import unittest

from stonemason.mason import *
from stonemason.mason.theme import MemThemeManager, PythonThemeLoader
from stonemason.mason.theme import SAMPLE_THEME

from tests import skipUnlessHasGDAL


@skipUnlessHasGDAL()
class TestMason(unittest.TestCase):
    def setUp(self):
        self._manager = MemThemeManager()

        loader = PythonThemeLoader(SAMPLE_THEME)
        loader.load_into(self._manager)

        self._mason = Mason()

    def test_load_theme(self):
        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)
        self._mason.load_theme(theme)

        self.assertIsNotNone(self._mason.get_map('sample'))
        self.assertRaises(DuplicatedMapError, self._mason.load_theme, theme)

    def test_get_maps(self):
        self.assertDictEqual(dict(), self._mason.get_maps())

        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)

        self._mason.load_theme(theme)
        self.assertIn('sample', self._mason.get_maps())

    def test_get_tile(self):
        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)
        self._mason.load_theme(theme)

        tile = self._mason.get_tile('sample', 0, 0, 0, 1, 'png')
        self.assertIsNotNone(tile)
