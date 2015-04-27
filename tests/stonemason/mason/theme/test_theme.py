# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/1/15'

import unittest

from stonemason.mason.theme import Theme


class TestMapTheme(unittest.TestCase):
    def setUp(self):
        self.expected = {
            'name': 'test',
            'metadata': {
                'title': 'It is test.'
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
        self.assertListEqual(list(), list(theme.map_sheets))

    def test_theme_from_dict(self):
        theme = Theme(**self.expected)

        self.assertEqual('test', theme.name)
        self.assertEqual({'title': 'It is test.'}, theme.metadata)

        for matrix in theme.map_sheets:
            self.assertEqual('image', matrix.maptype)
            self.assertEqual({'stride': 16}, matrix.pyramid)
            self.assertEqual({'format': 'PNG'}, matrix.tileformat)
            self.assertEqual({'prototype': 'null'}, matrix.storage)
            self.assertEqual({'prototype': 'null'}, matrix.renderer)


