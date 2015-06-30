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
        self.assertListEqual(list(), list(theme.schemas))

    def test_theme_from_dict(self):
        theme = Theme(**self.expected)

        self.assertEqual('test', theme.name)
        self.assertEqual({'title': 'It is test.'}, theme.metadata)

        for schema in theme.schemas:
            self.assertEqual('image', schema.maptype)
            self.assertEqual({'stride': 16}, schema.pyramid)
            self.assertEqual({'format': 'PNG'}, schema.tileformat)
            self.assertEqual({'prototype': 'null'}, schema.storage)
            self.assertEqual({'prototype': 'null'}, schema.renderer)


