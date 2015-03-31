# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import MemThemeManager
from stonemason.mason.theme import JsonThemeLoader, LocalThemeLoader

from stonemason.mason.theme import SAMPLE_THEME, SAMPLE_THEME_DIRECTORY

class TestJsonThemeLoader(unittest.TestCase):

    def test_load(self):
        m = MemThemeManager()

        loader = JsonThemeLoader(SAMPLE_THEME)
        loader.load_into(m)

        theme = m.get('sample')
        self.assertEqual('sample', theme.name)


class TestDirectoryThemeLoader(unittest.TestCase):

    def test_load(self):
        m = MemThemeManager()

        loader = LocalThemeLoader(SAMPLE_THEME_DIRECTORY)
        loader.load_into(m)

        theme = m.get('sample')
        self.assertEqual('sample', theme.name)
