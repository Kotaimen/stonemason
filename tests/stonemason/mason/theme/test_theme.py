# -*- encoding: utf-8 -*-

import unittest

from stonemason.mason.theme import *


class TestMetadataConfig(unittest.TestCase):
    def test_default(self):
        m = MetadataConfig()
        self.assertEqual('K&R', m.attribution)

    def test_attribution(self):
        m = MetadataConfig('dummy copyright')
        self.assertEqual('dummy copyright', m.attribution)


class TestPyramidConfig(unittest.TestCase):
    def test_default(self):
        m = PyramidConfig()

        self.assertEqual(range(0, 23), m.levels)
        self.assertEqual(1, m.stride)
        self.assertEqual('EPSG:4326', m.crs)
        self.assertEqual('EPSG:3857', m.proj)
        self.assertTupleEqual((-180, -85.0511, 180, 85.0511), m.boundary)

    def test_levels(self):
        m = PyramidConfig(levels=range(0, 5))
        self.assertEqual(range(0, 5), m.levels)

    def test_stride(self):
        m = PyramidConfig(stride=2)
        self.assertEqual(2, m.stride)

    def test_crs(self):
        m = PyramidConfig(crs='EPSG:4301')
        self.assertEqual('EPSG:4301', m.crs)

    def test_proj(self):
        m = PyramidConfig(proj='EPSG:4326', )
        self.assertEqual('EPSG:4326', m.proj)

    def test_boundary(self):
        m = PyramidConfig(boundary=(-45., -45., 45., 45.))
        self.assertEqual((-45., -45., 45., 45.), m.boundary)


class TestCacheConfig(unittest.TestCase):
    def test_default(self):
        m = CacheConfig()

        self.assertEqual('null', m.prototype)
        self.assertDictEqual(dict(), m.parameters)

    def test_prototype(self):
        m = CacheConfig(prototype='memcache')
        self.assertEqual('memcache', m.prototype)

    def test_paramters(self):
        m = CacheConfig(parameters=dict(hosts=['1.1.1.1']))
        self.assertDictEqual(dict(hosts=['1.1.1.1']), m.parameters)


class TestStorageConfig(unittest.TestCase):
    def test_default(self):
        m = StorageConfig()

        self.assertEqual('null', m.prototype)
        self.assertDictEqual(dict(), m.parameters)

    def test_prototype(self):
        m = StorageConfig(prototype='memcache')
        self.assertEqual('memcache', m.prototype)

    def test_paramters(self):
        m = StorageConfig(parameters=dict(hosts=['1.1.1.1']))
        self.assertDictEqual(dict(hosts=['1.1.1.1']), m.parameters)


class TestTheme(unittest.TestCase):
    def test_sample_theme(self):
        parser = JsonThemeParser()
        theme = parser.read_from_file(SAMPLE_THEME)[0]

        self.assertEqual('antique', theme.name)
        self.assertEqual('I am a sample.', theme.metadata.attribution)

        self.assertEqual(range(0, 23), theme.pyramid.levels)
        self.assertEqual(16, theme.pyramid.stride)
        self.assertEqual('EPSG:4326', theme.pyramid.crs)
        self.assertEqual('EPSG:3857', theme.pyramid.proj)
        self.assertTupleEqual(
            (-180, -85.0511, 180, 85.0511), theme.pyramid.boundary)

        self.assertEqual('null', theme.cache.prototype)
        self.assertDictEqual(dict(), theme.cache.parameters)

        self.assertEqual('disk', theme.storage.prototype)
        self.assertDictEqual(
            dict(
                root="/Users/ray/proj/python/stonemason/stonemason/mason/theme/samples/antique",
                dir_mode="legacy"
            ),
            theme.storage.parameters
        )
