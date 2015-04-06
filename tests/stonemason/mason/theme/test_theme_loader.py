# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import MemThemeManager
from stonemason.mason.theme import FileSystemThemeLoader

from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY


class TestFileSystemThemeLoader(unittest.TestCase):
    def test_load(self):
        m = MemThemeManager()

        loader = FileSystemThemeLoader(SAMPLE_THEME_DIRECTORY)
        loader.load_into(m)

        self.assertTrue(m.has('sample'))
        self.assertTrue(m.has('sample.hd'))

