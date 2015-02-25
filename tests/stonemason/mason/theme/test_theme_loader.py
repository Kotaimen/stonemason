# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import DictThemeManager
from stonemason.mason.theme import JsonThemeLoader, DirectoryThemeLoader

from stonemason.mason.theme import SAMPLE_THEME, SAMPLE_THEME_DIRECTORY

class TestJsonThemeLoader(unittest.TestCase):

    def test_load(self):
        m = DictThemeManager()

        loader = JsonThemeLoader(SAMPLE_THEME)
        loader.load(m)

        theme = m.get('antique')
        self.assertEqual('antique', theme.name)


class TestDirectoryThemeLoader(unittest.TestCase):

    def test_load(self):
        m = DictThemeManager()

        loader = DirectoryThemeLoader(SAMPLE_THEME_DIRECTORY)
        loader.load(m)

        theme = m.get('antique')
        self.assertEqual('antique', theme.name)
