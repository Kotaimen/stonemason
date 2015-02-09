# -*- encoding: utf-8 -*-
"""
    tests.stonemason.service.tileserver.test_tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test interfaces of the tile server application.

"""


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
        resp = self.client.get('/tile/nanook/0/0/0.png')
        self.assertEqual(resp.status_code, 404)
