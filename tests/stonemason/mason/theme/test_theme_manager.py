# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import ThemeManagerError, MapTheme, MemThemeManager


class TestMemThemeManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemThemeManager()

    def test_put_theme(self):
        theme = MapTheme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))

    def test_put_dup_theme(self):
        theme = MapTheme()
        self.manager.put(theme.name, theme)
        self.assertRaises(
            ThemeManagerError, self.manager.put, theme.name, theme)

    def test_get_theme(self):
        theme = MapTheme()
        self.manager.put(theme.name, theme)
        self.assertEqual(theme, self.manager.get(theme.name))
        self.assertIsNone(self.manager.get('not exists'))

    def test_has_theme(self):
        theme = MapTheme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))
        self.assertFalse(self.manager.has('not exists'))

    def test_delete_theme(self):
        theme = MapTheme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))

        self.manager.delete(theme.name)
        self.assertFalse(self.manager.has(theme.name))

    def test_iteritems(self):
        theme1 = MapTheme(name='theme1')
        theme2 = MapTheme(name='theme2')

        self.manager.put(theme1.name, theme1)
        self.manager.put(theme2.name, theme2)

        themes = list(iter(self.manager))
        self.assertIn(theme1.name, themes)
        self.assertIn(theme2.name, themes)
        self.assertEqual(2, len(themes))
