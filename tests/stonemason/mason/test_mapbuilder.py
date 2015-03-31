# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

import shutil
import tempfile
import unittest
import moto
import boto

from stonemason.mason.theme import Theme
from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.mason.mapbuilder import MapBuilder, make_cluster_storage, \
    make_metatile_renderer
from stonemason.provider.tileprovider import HybridTileProvider
from stonemason.provider.tilestorage import ClusterStorage
from stonemason.renderer.tilerenderer import MetaTileRenderer

from tests import skipUnlessHasGDAL


class TestMakeClusterStorage(unittest.TestCase):
    def test_make_null_storage(self):
        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        prototype = 'null'
        parameters = {}

        storage = make_cluster_storage(prototype, bundle, pyramid, **parameters)

        self.assertIsInstance(storage, ClusterStorage)

    def test_make_disk_storage(self):
        root = tempfile.mkdtemp()

        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        prototype = 'disk'
        parameters = {'root': root}

        storage = make_cluster_storage(prototype, bundle, pyramid, **parameters)

        self.assertIsInstance(storage, ClusterStorage)

        shutil.rmtree(root, ignore_errors=True)

    def test_make_s3_storage(self):
        with moto.mock_s3():
            self.conn = boto.connect_s3()
            self.conn.create_bucket('test_storage')

            maptype = MapType('image')
            tileformat = TileFormat('JPEG')
            bundle = FormatBundle(maptype, tileformat)

            pyramid = Pyramid()

            prototype = 's3'
            parameters = {
                'bucket': 'test_storage',
                'prefix': 'testlayer',
            }

            storage = make_cluster_storage(
                prototype=prototype,
                pyramid=pyramid,
                bundle=bundle,
                **parameters)

            self.assertIsInstance(storage, ClusterStorage)


@skipUnlessHasGDAL()
class TestMakeTileRenderer(unittest.TestCase):
    def test_make_image_tilerenderer(self):
        maptype = MapType('image')
        tileformat = TileFormat('JPEG')
        bundle = FormatBundle(maptype, tileformat)

        pyramid = Pyramid()

        prototype = 'image'
        parameters = {
            'layers': {
                'root': {
                    'type': 'dummy'
                }
            }
        }

        renderer = make_metatile_renderer(
            prototype, bundle, pyramid, **parameters)

        self.assertIsInstance(renderer, MetaTileRenderer)


@skipUnlessHasGDAL()
class TestMapBuilder(unittest.TestCase):
    def setUp(self):
        self._builder = MapBuilder()

    def test_build_map_from_theme(self):
        theme = Theme(name='test')

        mason_map = self._builder.build_from_theme(theme)
        self.assertEqual('test', mason_map.name)
        self.assertIsInstance(mason_map.metadata, dict)
        self.assertIsInstance(mason_map.provider, HybridTileProvider)
