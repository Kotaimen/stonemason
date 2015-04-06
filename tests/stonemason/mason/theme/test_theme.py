# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/1/15'

import unittest

from stonemason.mason.theme import MapTheme


class TestMapTheme(unittest.TestCase):
    def setUp(self):
        self.expected = {
            'name': 'test',
            'metadata': {
                'title': 'It is test.'
            },
            'provider': {
                'maptype': 'image',
                'tileformat': {
                    'format': 'PNG'
                },
                'pyramid': {
                    'stride': 16
                },
                'storage': {
                    'prototype': 'null'
                },
                'renderer': {
                    'prototype': 'null'
                }

            }
        }

    def test_default_theme(self):
        theme = MapTheme()
        self.assertEqual('', theme.name)
        self.assertEqual('image', theme.maptype)
        self.assertEqual(dict(), theme.pyramid)
        self.assertEqual(dict(format='PNG'), theme.tileformat)
        self.assertEqual(dict(prototype='null'), theme.storage)
        self.assertEqual(dict(prototype='null'), theme.renderer)

    def test_theme_from_dict(self):
        theme = MapTheme(**self.expected)

        self.assertEqual('test', theme.name)
        self.assertEqual({'title': 'It is test.'}, theme.metadata)
        self.assertEqual('image', theme.maptype)
        self.assertEqual({'stride': 16}, theme.pyramid)
        self.assertEqual({'format': 'PNG'}, theme.tileformat)
        self.assertEqual({'prototype': 'null'}, theme.storage)
        self.assertEqual({'prototype': 'null'}, theme.renderer)


