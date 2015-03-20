# -*- encoding: utf-8 -*-

import unittest

from stonemason.mason.theme import *


class TestThemeMetadata(unittest.TestCase):
    def setUp(self):
        self._expected = dict(
            attribution='dummy copyright',
            version='0.0.1',
            description='a sample',
            thumbnail='http://example.com/1.jpeg',
            center=[1, 1],
            center_zoom=5
        )

    def test_default(self):
        m = ThemeMetadata(name='metadata')
        self.assertEqual('K&R', m.attribution)
        self.assertEqual('', m.version)
        self.assertEqual('', m.description)
        self.assertEqual('', m.thumbnail)
        self.assertEqual([0, 0], m.center)
        self.assertEqual(4, m.center_zoom)

    def test_init(self):
        m = ThemeMetadata(name='metadata', **self._expected)

        self.assertEqual('dummy copyright', m.attribution)
        self.assertEqual('0.0.1', m.version)
        self.assertEqual('a sample', m.description)
        self.assertEqual('http://example.com/1.jpeg', m.thumbnail)
        self.assertEqual([1, 1], m.center)
        self.assertEqual(5, m.center_zoom)


class TestThemePyramid(unittest.TestCase):
    def setUp(self):
        self._expected = dict(
            levels=range(0, 5),
            stride=2,
            geogcs='EPSG:4301',
            projcs='EPSG:4326',
            geogbounds=(-45., -45., 45., 45.),
            projbounds=(-44., -44., 44., 44.))

    def test_default(self):
        m = ThemePyramid(name='pyramid')

        self.assertEqual(list(range(0, 23)), m.levels)
        self.assertEqual(1, m.stride)
        self.assertEqual('WGS84', m.geogcs)
        self.assertEqual('EPSG:3857', m.projcs)
        self.assertTupleEqual((-180, -85.0511, 180, 85.0511), m.geogbounds)

    def test_init(self):
        m = ThemePyramid(name='pyramid', **self._expected)

        self.assertEqual(range(0, 5), m.levels)
        self.assertEqual(2, m.stride)
        self.assertEqual('EPSG:4301', m.geogcs)
        self.assertEqual('EPSG:4326', m.projcs)
        self.assertEqual((-45., -45., 45., 45.), m.geogbounds)
        self.assertEqual((-44., -44., 44., 44.), m.projbounds)


class TestCacheTheme(unittest.TestCase):
    def setUp(self):
        self._expected = dict(
            prototype='memcache',
            parameters=dict(hosts=['1.1.1.1']))

    def test_default(self):
        m = ThemeCache(name='cache')
        self.assertEqual('null', m.prototype)
        self.assertDictEqual(dict(), m.parameters)

    def test_init(self):
        m = ThemeCache(name='cache', **self._expected)
        self.assertEqual('memcache', m.prototype)
        self.assertDictEqual(dict(hosts=['1.1.1.1']), m.parameters)


class TestStorageTheme(unittest.TestCase):
    def setUp(self):
        self._expected = dict(
            prototype='disk',
            parameters=dict(root='.'))

    def test_default(self):
        m = ThemeStorage(name='storage')
        self.assertEqual('null', m.prototype)
        self.assertDictEqual(dict(), m.parameters)

    def test_init(self):
        m = ThemeStorage(name='storage', **self._expected)
        self.assertEqual('disk', m.prototype)
        self.assertDictEqual(dict(root='.'), m.parameters)


class TestTheme(unittest.TestCase):
    def setUp(self):
        self._expected = dict(
            name='test',
            metadata=dict(version='1.0.0'),
            pyramid=dict(levels=[0, 1, 2]),
            cache=dict(prototype='memcache'),
            storage=dict(prototype='disk', parameters=dict(root='.'))
        )

    def test_default(self):
        t = Theme()

        self.assertEqual(
            'default', t.name)
        self.assertEqual(
            ThemeMetadata(name='dummy').attributes, t.metadata.attributes)
        self.assertEqual(
            ThemePyramid(name='dummy').attributes, t.pyramid.attributes)
        self.assertEqual(
            ThemeCache(name='dummy').attributes, t.cache.attributes)
        self.assertEqual(
            ThemeStorage(name='dummy').attributes, t.storage.attributes)

    def test_init(self):
        t = Theme(**self._expected)

        self.assertEqual('test', t.name)
        self.assertEqual(
            self._expected['metadata']['version'], t.metadata.version)
        self.assertEqual(
            self._expected['pyramid']['levels'], t.pyramid.levels)
        self.assertEqual(
            self._expected['cache']['prototype'], t.cache.prototype)
        self.assertEqual(
            self._expected['storage']['prototype'], t.storage.prototype)
        self.assertEqual(
            self._expected['storage']['parameters'], t.storage.parameters)
