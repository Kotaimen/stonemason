# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import unittest

from stonemason.mason.metadata import Metadata


class TestMetadata(unittest.TestCase):
    def test_metadata(self):
        m = Metadata(
            title='test',
            version='0.0.1',
            abstract='This is a test.',
            attribution='K&R',
            origin=(0, 0),
            origin_zoom=6
        )

        self.assertEqual('test', m.title)
        self.assertEqual('0.0.1', m.version)
        self.assertEqual('This is a test.', m.abstract)
        self.assertEqual('K&R', m.attribution)
        self.assertEqual((0, 0), m.origin)
        self.assertEqual(6, m.origin_zoom)

    def test_default_metadata(self):
        m = Metadata()

        self.assertEqual('', m.title)
        self.assertEqual('', m.version)
        self.assertEqual('', m.abstract)
        self.assertEqual('', m.attribution)
        self.assertEqual((0, 0), m.origin)
        self.assertEqual(4, m.origin_zoom)
