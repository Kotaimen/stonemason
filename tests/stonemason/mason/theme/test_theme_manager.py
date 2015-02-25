# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import Theme, DictThemeManager


class TestThemeManager(unittest.TestCase):
    def setUp(self):
        self.manager = DictThemeManager()

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

    def test_list_themes(self):
        theme = Theme()
        self.manager.put(theme.name, theme)
        self.assertListEqual(['default'], self.manager.list())
