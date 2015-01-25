# -*- encoding: utf-8 -*-


import unittest

from stonemason.mason.theme import MetadataBlock, MetadataValueError


class TestMetadataBlock(unittest.TestCase):
    def test_name(self):
        # test default name
        metadata = MetadataBlock()
        self.assertEqual('default', metadata.name)

        # test specified name
        metadata = MetadataBlock(name='test')
        self.assertEqual('test', metadata.name)

        # test bad names
        self.assertRaises(MetadataValueError, MetadataBlock, name=1)
        self.assertRaises(MetadataValueError, MetadataBlock, name='4d')
        self.assertRaises(MetadataValueError, MetadataBlock, name='d~~~')

    def test_crs(self):
        # test default crs
        metadata = MetadataBlock()
        self.assertEqual('epsg:3857', metadata.crs)

        # test specified crs
        metadata = MetadataBlock(crs='wgs84')
        self.assertEqual('wgs84', metadata.crs)

        # test bad crs
        self.assertRaises(MetadataValueError, MetadataBlock, crs=1)

    def test_scale(self):
        # test default scale
        metadata = MetadataBlock()
        self.assertEqual(1, metadata.scale)

        # test specified scale
        metadata = MetadataBlock(scale=3)
        self.assertEqual(3, metadata.scale)

        # test bad scale
        self.assertRaises(MetadataValueError, MetadataBlock, scale='blabla')
        self.assertRaises(MetadataValueError, MetadataBlock, scale=6)
        self.assertRaises(MetadataValueError, MetadataBlock, scale=0)

    def test_buffer(self):
        # test default buffer
        metadata = MetadataBlock()
        self.assertEqual(0, metadata.buffer)

        # test specified buffer
        metadata = MetadataBlock(buffer=32)
        self.assertEqual(32, metadata.buffer)

        # test buffer with scale
        metadata = MetadataBlock(buffer=32, scale=2)
        self.assertEqual(64, metadata.buffer)

        # test bad buffer
        self.assertRaises(MetadataValueError, MetadataBlock, buffer='blabla')
        self.assertRaises(MetadataValueError, MetadataBlock, buffer=-1)

    def test_stride(self):
        # test default stride
        metadata = MetadataBlock()
        self.assertEqual(1, metadata.stride)

        # test specified stride
        metadata = MetadataBlock(stride=2)
        self.assertEqual(2, metadata.stride)

        # test bad stride
        self.assertRaises(MetadataValueError, MetadataBlock, stride='1')
        self.assertRaises(MetadataValueError, MetadataBlock, stride=3)

    def test_format(self):
        # test default format
        metadata = MetadataBlock()
        self.assertEqual('png', metadata.format)

        # test specified format
        metadata = MetadataBlock(format='jpeg')
        self.assertEqual('jpeg', metadata.format)

        # test bad format
        self.assertRaises(MetadataValueError, MetadataBlock, format=1)
        self.assertRaises(MetadataValueError, MetadataBlock, format='abc')

    def test_format_options(self):
        # test default format options
        metadata = MetadataBlock()
        self.assertEqual(None, metadata.format_options)

        # test specified format options
        metadata = MetadataBlock(format_options=dict(quality=85))
        self.assertEqual(dict(quality=85), metadata.format_options)

        # test bad format options
        self.assertRaises(MetadataValueError, MetadataBlock, format_options=1)
        self.assertRaises(MetadataValueError, MetadataBlock, format_options='1')

    def test_attribution(self):
        # test default attribution
        metadata = MetadataBlock()
        self.assertEqual('', metadata.attribution)

        # test specified attribution
        metadata = MetadataBlock(attribution='copyright@stonemason')
        self.assertEqual('copyright@stonemason', metadata.attribution)

        # test bad attribution
        self.assertRaises(MetadataValueError, MetadataBlock, attribution=1)

    def test_tag(self):
        # test default tag
        metadata = MetadataBlock()
        self.assertEqual('default', metadata.tag)

        metadata = MetadataBlock(name='bob', scale=2)
        self.assertEqual('bob@2x', metadata.tag)

    def test_to_json(self):

        metadata = MetadataBlock()

        expected = {
            "crs": "epsg:3857",
            "scale": 1,
            "attribution": "",
            "name": "default",
            "format": "png",
            "buffer": 0,
            "format_options": None,
            "stride": 1
        }

        import json
        self.assertDictEqual(expected, json.loads(metadata.to_json()))

    def test_repr(self):

        metadata = MetadataBlock()

        expected = "MetadataBlock(name='default', crs='epsg:3857', scale=1, " \
            "buffer=0, stride=1, format='png', format_options=None, " \
            "attribution='')"

        self.assertEqual(expected, repr(metadata))
