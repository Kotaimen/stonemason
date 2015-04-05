# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import MapTheme
from stonemason.mason.theme import MemThemeManager
from stonemason.mason.theme import PythonThemeLoader, LocalThemeLoader

from stonemason.mason.theme import SAMPLE_THEME, SAMPLE_THEME_DIRECTORY


class TestPyThemeLoader(unittest.TestCase):
    def test_load(self):
        m = MemThemeManager()

        loader = PythonThemeLoader(SAMPLE_THEME)
        loader.load_into(m)

        theme = m.get('sample')
        self.assertIsInstance(theme, MapTheme)


class TestLocalThemeLoader(unittest.TestCase):
    def test_load(self):
        m = MemThemeManager()

        loader = LocalThemeLoader(SAMPLE_THEME_DIRECTORY)
        loader.load_into(m)

        theme = m.get('sample')
        self.assertIsInstance(theme, MapTheme)
