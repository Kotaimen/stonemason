# -*- encoding: utf-8 -*-
"""
    tests.stonemason.service.tileserver.test_tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test interfaces of the tile server application.

"""

import six
import json
import unittest
from stonemason.service.tileserver import StoneMasonApp


class TestStoneMasonApp(unittest.TestCase):
    def setUp(self):
        app = StoneMasonApp()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True

        self.client = app.test_client()

    def test_get_theme(self):
        resp = self.client.get('/themes/brick')
        self.assertDictEqual(
            {
                six.u("result"): {
                    six.u("name"): six.u("brick")
                }
            },
            json.loads(resp.data.decode('utf-8'))
        )

    def test_list_themes(self):
        resp = self.client.get('/themes')
        self.assertDictEqual(
            {
                six.u("result"): []
            },
            json.loads(resp.data.decode('utf-8'))
        )

    def test_get_tile(self):
        resp = self.client.get('/tile/brick/0/0/0.png')
        self.assertEqual(
            six.b("Tile(brick, 0, 0, 0, 1x, png)"),
            resp.data
        )

        resp = self.client.get('/tile/brick/0/0/0@2x.png')
        self.assertEqual(
            six.b("Tile(brick, 0, 0, 0, 2x, png)"),
            resp.data
        )
