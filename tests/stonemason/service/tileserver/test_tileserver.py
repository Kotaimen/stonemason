# -*- encoding: utf-8 -*-
"""
    tests.stonemason.service.tileserver.test_tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test interfaces of the tile server application.

"""

import os
import unittest
from stonemason.service.tileserver import AppBuilder


class TestExample(unittest.TestCase):
    def setUp(self):
        os.environ['EXAMPLE_APP_MODE'] = 'development'

        app = AppBuilder().build(config='settings.py')
        self.client = app.test_client()

    def test_app(self):
        resp = self.client.get('/')
        self.assertEqual(b'Hello World!', resp.data)
