# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/1/15'

import unittest

from stonemason.mason_.theme import Theme


class TestMapTheme(unittest.TestCase):
    def setUp(self):
        self.expected = {
            'name': 'test',
            'metadata': {
                'title': 'It is test.'
            },
            'maptype': 'image',
            'tileformat': {
                'format': 'PNG'
            },
            'pyramid': {
                'stride': 16
            },
            'tilematrix_set': [
                {
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
                },
            ]
        }

    def test_default_theme(self):
        theme = Theme()
        self.assertIsNone(theme.name)
        self.assertIsNone(theme.maptype)
        self.assertIsNone(theme.pyramid)
        self.assertIsNone(theme.tileformat)
        self.assertListEqual(list(), list(theme.tilematrix_set))

    def test_theme_from_dict(self):
        theme = Theme(**self.expected)

        self.assertEqual('test', theme.name)
        self.assertEqual({'title': 'It is test.'}, theme.metadata)
        self.assertEqual('image', theme.maptype)
        self.assertEqual({'stride': 16}, theme.pyramid)
        self.assertEqual({'format': 'PNG'}, theme.tileformat)

        for matrix in theme.tilematrix_set:
            self.assertEqual('image', matrix.maptype)
            self.assertEqual({'stride': 16}, matrix.pyramid)
            self.assertEqual({'format': 'PNG'}, matrix.tileformat)
            self.assertEqual({'prototype': 'null'}, matrix.storage)
            self.assertEqual({'prototype': 'null'}, matrix.renderer)


