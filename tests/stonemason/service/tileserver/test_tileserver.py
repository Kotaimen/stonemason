# -*- encoding: utf-8 -*-
"""
    tests.stonemason.service.tileserver.test_tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test interfaces of the tile server application.

"""

import six
import json
import unittest

from stonemason.service.tileserver import TileServerApp
from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY


class TestTileServerApp(unittest.TestCase):
    def setUp(self):
        self.app = TileServerApp(STONEMASON_THEMES=SAMPLE_THEME_DIRECTORY)
        self.app.config['DEBUG'] = True
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()

    def test_get_tile(self):
        resp = self.client.get('/tiles/nanook/0/0/0.png')
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get('/tiles/antique/0/0/0.png')
        self.assertEqual(resp.status_code, 404)

    def test_get_theme(self):
        resp = self.client.get('/themes/antique')
        data = json.loads(resp.data.decode('utf-8'))

        desp = data['result']

        self.assertIn('name', desp)
        self.assertIn('pyramid', desp)
        self.assertIn('metadata', desp)
        self.assertIn('cache', desp)
        self.assertIn('storage', desp)

    def test_get_themes(self):
        resp = self.client.get('/themes')
        data = json.loads(resp.data.decode('utf-8'))

        for desp in data['result']:
            self.assertIn('name', desp)
            self.assertIn('pyramid', desp)
            self.assertIn('metadata', desp)
            self.assertIn('cache', desp)
            self.assertIn('storage', desp)
