# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import Theme, MemThemeManager


class TestMemThemeManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemThemeManager()

    def test_put_theme(self):
        theme = Theme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))

    def test_get_theme(self):
        theme = Theme()
        self.manager.put(theme.name, theme)
        self.assertEqual(theme, self.manager.get(theme.name))
        self.assertIsNone(self.manager.get('dummy'))

    def test_has_theme(self):
        theme = Theme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))
        self.assertFalse(self.manager.has('dummy'))

    def test_delete_theme(self):
        theme = Theme()
        self.manager.put(theme.name, theme)
        self.assertTrue(self.manager.has(theme.name))

        self.manager.delete(theme.name)
        self.assertFalse(self.manager.has(theme.name))

    def test_iternames(self):
        theme1 = Theme(name='theme1')
        theme2 = Theme(name='theme2')

        self.manager.put(theme1.name, theme1)
        self.manager.put(theme2.name, theme2)

        names = list(self.manager.iternames())
        self.assertIn(theme1.name, names)
        self.assertIn(theme2.name, names)
        self.assertEqual(2, len(names))

    def test_iterthemes(self):
        theme1 = Theme(name='theme1')
        theme2 = Theme(name='theme2')

        self.manager.put(theme1.name, theme1)
        self.manager.put(theme2.name, theme2)

        themes = list(self.manager.iterthemes())
        self.assertIn(theme1, themes)
        self.assertIn(theme2, themes)
        self.assertEqual(2, len(themes))

    def test_iteritems(self):
        theme1 = Theme(name='theme1')
        theme2 = Theme(name='theme2')

        self.manager.put(theme1.name, theme1)
        self.manager.put(theme2.name, theme2)

        themes = list(iter(self.manager))
        self.assertIn((theme1.name, theme1), themes)
        self.assertIn((theme2.name, theme2), themes)
        self.assertEqual(2, len(themes))