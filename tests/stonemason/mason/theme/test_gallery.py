# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason_.theme import Theme, MemGallery


class TestMemThemeManager(unittest.TestCase):
    def setUp(self):
        self.gallery = MemGallery()

    def test_put_theme(self):
        theme = Theme()
        self.gallery.put(theme.name, theme)
        self.assertTrue(self.gallery.has(theme.name))

    def test_get_theme(self):
        theme = Theme()
        self.gallery.put(theme.name, theme)
        self.assertEqual(theme, self.gallery.get(theme.name))
        self.assertIsNone(self.gallery.get('not exists'))

    def test_has_theme(self):
        theme = Theme()
        self.gallery.put(theme.name, theme)
        self.assertTrue(self.gallery.has(theme.name))
        self.assertFalse(self.gallery.has('not exists'))

    def test_delete_theme(self):
        theme = Theme()
        self.gallery.put(theme.name, theme)
        self.assertTrue(self.gallery.has(theme.name))

        self.gallery.delete(theme.name)
        self.assertFalse(self.gallery.has(theme.name))

    def test_iteritems(self):
        theme1 = Theme(name='theme1')
        theme2 = Theme(name='theme2')

        self.gallery.put(theme1.name, theme1)
        self.gallery.put(theme2.name, theme2)

        themes = list(iter(self.gallery))
        self.assertIn(theme1.name, themes)
        self.assertIn(theme2.name, themes)
        self.assertEqual(2, len(themes))
