# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/24/15'

import unittest

from stonemason.mason.theme import Theme
from stonemason.mason.builder import TileProviderFactory
from stonemason.provider.tileprovider import TileProvider


class TestTileProviderFactory(unittest.TestCase):

    def test_create_from_theme(self):
        theme = Theme()

        tag = theme.name
        factory = TileProviderFactory()
        provider = factory.create_from_theme(tag, theme)

        self.assertIsInstance(provider, TileProvider)
        self.assertEqual('default', provider.tag)

        self.assertDictEqual(theme.metadata.attributes, provider.metadata)

        self.assertEqual(theme.pyramid.levels, provider.pyramid.levels)
        self.assertEqual(theme.pyramid.stride, provider.pyramid.stride)
        self.assertEqual(theme.pyramid.geogcs, provider.pyramid.geogcs)
        self.assertEqual(theme.pyramid.projcs, provider.pyramid.projcs)
        self.assertEqual(theme.pyramid.geogbounds, provider.pyramid.geogbounds)
        self.assertEqual(theme.pyramid.projbounds, provider.pyramid.projbounds)

        self.assertIsNone(provider.get_tile(0, 0, 0))
