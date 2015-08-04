# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/4/15'

import unittest

from stonemason.renderer.cartographer.imagery import *
from stonemason.renderer import RenderContext
from stonemason.pyramid import MetaTileIndex

class TestDiskStorageLayer(unittest.TestCase):
    def setUp(self):
        self.layer = DiskStorageLayer(
            'test',
            maptype='image',
            tileformat=dict(format='PNG'),
            root='/Users/ray/proj/python/stonemason/stonemason/mason/theme/samples/sample_world/cache/sample')

    def test_render(self):

        crs = """+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"""
        envelope = (-20037508.34, -20037508.34, 20037508.34, 20037508.34)
        size = (256, 256)

        meta_index = MetaTileIndex(0, 0, 0, stride=4)

        context = RenderContext(map_proj=crs,
                                map_bbox=envelope,
                                map_size=size,
                                scale_factor=1,
                                meta_index=meta_index)

        feature = self.layer.render(context)

        image = feature.data

        self.assertTrue(size, image.size)
