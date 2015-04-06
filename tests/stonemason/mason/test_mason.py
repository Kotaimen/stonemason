# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/3/15'

import unittest

from stonemason.mason import *
from stonemason.mason.theme import MemThemeManager, FileSystemThemeLoader
from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY
from stonemason.provider.tileprovider import NullTileProvider

from tests import skipUnlessHasGDAL


class DummyMasonMap(MasonMap):
    def __init__(self, name='dummy'):
        MasonMap.__init__(
            self, name, metadata=Metadata(), provider=NullTileProvider())


@skipUnlessHasGDAL()
class TestMason(unittest.TestCase):
    def setUp(self):
        self._manager = MemThemeManager()

        loader = FileSystemThemeLoader(SAMPLE_THEME_DIRECTORY)
        loader.load_into(self._manager)

        self._mason = Mason()

    def test_load_map_from_theme(self):
        theme = self._manager.get('sample')
        self.assertIsNotNone(theme)

        self._mason.load_map_from_theme(theme)

        self.assertIsNotNone(self._mason.get_map('sample'))
        self.assertRaises(MasonError, self._mason.load_map_from_theme, theme)

    def test_put_get_map(self):
        mason_map = DummyMasonMap()
        self._mason.put_map(mason_map.name, mason_map)

        mason_map = self._mason.get_map(mason_map.name)
        self.assertIsNotNone(mason_map)

    def test_has_map(self):
        mason_map = DummyMasonMap()

        self._mason.put_map(mason_map.name, mason_map)
        self.assertTrue(self._mason.has_map(mason_map.name))
        self.assertFalse(self._mason.has_map('not exists'))

    def test_iter_maps(self):
        mason_map1 = DummyMasonMap('test1')
        mason_map2 = DummyMasonMap('test2')
        mason_map3 = DummyMasonMap('test3')

        self._mason.put_map(mason_map1.name, mason_map1)
        self._mason.put_map(mason_map2.name, mason_map2)
        self._mason.put_map(mason_map3.name, mason_map3)

        collection = list((m for m in self._mason))
        self.assertIn('test1', collection)
        self.assertIn('test2', collection)
        self.assertIn('test3', collection)

    def test_get_tile(self):
        mason_map = DummyMasonMap()
        self._mason.put_map(mason_map.name, mason_map)

        tile = self._mason.get_tile('dummy', 0, 0, 0)
        self.assertIsNone(tile)
