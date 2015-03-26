# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/25/15'

import unittest

from stonemason.mason.theme import Theme
from stonemason.renderer.tilerenderer import ImageMetaTileRenderer
from stonemason.renderer.tilerenderer import MetaTileRendererBuilder


class TestMetaTileRendererBuilder(unittest.TestCase):
    def test_build_base_renderer(self):
        d = {
            'design': {
                'layers': {
                    'root': {
                        'type': 'dummy',
                    }
                }
            }
        }

        theme = Theme(**d)

        builder = MetaTileRendererBuilder()
        renderer = builder.build(theme)

        self.assertIsInstance(renderer, ImageMetaTileRenderer)

    def test_build_transform_renderer(self):
        d = {
            'design': {
                'layers': {
                    'layer1': {
                        'type': 'dummy'
                    },
                    'root': {
                        'type': 'dummy',
                        'source': 'layer1'
                    }
                }
            }
        }

        theme = Theme(**d)

        builder = MetaTileRendererBuilder()
        renderer = builder.build(theme)

        self.assertIsInstance(renderer, ImageMetaTileRenderer)

    def test_build_composite_renderer(self):
        d = {
            'design': {
                'layers': {
                    'layer1': {
                        'type': 'dummy'
                    },
                    'layer2': {
                        'type': 'dummy'
                    },
                    'root': {
                        'type': 'dummy',
                        'sources': ['layer1', 'layer2']
                    }
                }
            }
        }

        theme = Theme(**d)

        builder = MetaTileRendererBuilder()
        renderer = builder.build(theme)

        self.assertIsInstance(renderer, ImageMetaTileRenderer)
