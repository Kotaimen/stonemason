# -*- encoding: utf-8 -*-
"""
    tests.stonemason.service.tileserver.test_tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test interfaces of the tile server application.

"""
import os
import json
import unittest

from stonemason.service.tileserver import TileServerApp
from stonemason.mason.theme import SAMPLE_THEME_DIRECTORY

from tests import skipUnlessHasGDAL


class TestTileServerAppSetup(unittest.TestCase):
    def test_config_from_default_settings(self):
        app = TileServerApp()
        self.assertEqual(False, app.config['STONEMASON_DEBUG'])
        self.assertEqual(False, app.config['STONEMASON_TESTING'])
        self.assertEqual('.', app.config['STONEMASON_THEMES'])
        self.assertEqual(None, app.config['STONEMASON_CACHE'])
        self.assertEqual(0, app.config['STONEMASON_VERBOSE'])

    def test_config_from_pyfile(self):
        self.assertRaises(IOError, TileServerApp, 'settings.py')

    def test_config_from_env_variables(self):
        os.environ['STONEMASON_DEBUG'] = 'True'
        app = TileServerApp()
        self.assertIn('STONEMASON_DEBUG', app.config)

    def test_config_from_cmd_varables(self):
        app = TileServerApp(STONEMASON_DEBUG=True)
        self.assertIn('STONEMASON_DEBUG', app.config)


@skipUnlessHasGDAL()
class TestTileServerApp(unittest.TestCase):
    def setUp(self):
        self.app = TileServerApp(
            STONEMASON_THEMES=SAMPLE_THEME_DIRECTORY,
            STONEMASON_TESTING=True)

        self.client = self.app.test_client()

    def test_get_themes(self):
        resp = self.client.get('/themes')
        data = json.loads(resp.data.decode('utf-8'))

        themes = data['result']

        for theme in themes:
            self.assertIn('name', theme)
            self.assertIn('metadata', theme)
            self.assertIn('tilematrix_set', theme)


    def test_get_theme(self):
        resp = self.client.get('/themes/sample')
        data = json.loads(resp.data.decode('utf-8'))

        theme = data['result']

        self.assertIn('name', theme)
        self.assertIn('metadata', theme)
        self.assertIn('tilematrix_set', theme)
        
    def test_get_tile(self):
        resp = self.client.get('/tiles/antique/1/1/1.jpg')
        self.assertEqual(404, resp.status_code)

    def test_get_map(self):
        resp = self.client.get('/maps/sample')
        self.assertEqual(200, resp.status_code)

    def test_health_check(self):
        resp = self.client.get('/health_check')
        self.assertEqual(200, resp.status_code)

    def test_admin(self):
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code)
