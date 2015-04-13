# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason_.theme import MemGallery
from stonemason.mason_.theme import FileSystemCurator

from stonemason.mason_.theme import SAMPLE_THEME_DIRECTORY


class TestFileSystemThemeLoader(unittest.TestCase):
    def test_load(self):
        m = MemGallery()

        loader = FileSystemCurator(SAMPLE_THEME_DIRECTORY)
        loader.add_to(m)

        self.assertTrue(m.has('sample'))
        self.assertTrue(m.has('sample.hd'))

