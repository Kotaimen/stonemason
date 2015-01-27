# -*- encoding: utf-8 -*-

import json
import unittest

from stonemason.mason.theme import *


class TestMetadataBlock(unittest.TestCase):
    def test_name(self):
        # test default name
        metadata = MetadataBlock()
        self.assertEqual('default', metadata.name)

        # test specified name
        metadata = MetadataBlock(name='test')
        self.assertEqual('test', metadata.name)

        # test bad names
        self.assertRaises(FieldTypeError, MetadataBlock, name=1)
        self.assertRaises(ValidationError, MetadataBlock, name='4d')
        self.assertRaises(ValidationError, MetadataBlock, name='d~~~')

    def test_crs(self):
        # test default crs
        metadata = MetadataBlock()
        self.assertEqual('EPSG:3857', metadata.crs)

        # test specified crs
        metadata = MetadataBlock(crs='WGS84')
        self.assertEqual('WGS84', metadata.crs)

        # test bad crs
        self.assertRaises(FieldTypeError, MetadataBlock, crs=1)

    def test_scale(self):
        # test default scale
        metadata = MetadataBlock()
        self.assertEqual([1], metadata.scale)

        # test specified scale
        metadata = MetadataBlock(scale=3)
        self.assertEqual([3], metadata.scale)

        metadata = MetadataBlock(scale=[1, 2])
        self.assertEqual([1, 2], metadata.scale)

        # test bad scale
        self.assertRaises(FieldTypeError, MetadataBlock, scale='bla')
        self.assertRaises(ValidationError, MetadataBlock, scale=6)
        self.assertRaises(ValidationError, MetadataBlock, scale=0)

    def test_buffer(self):
        # test default buffer
        metadata = MetadataBlock()
        self.assertEqual(0, metadata.buffer())

        # test specified buffer
        metadata = MetadataBlock(buffer=32)
        self.assertEqual(32, metadata.buffer())

        # test buffer with scale
        metadata = MetadataBlock(buffer=32, scale=2)
        self.assertEqual(64, metadata.buffer(scale=2))

        # test bad buffer
        self.assertRaises(FieldTypeError, MetadataBlock, buffer='bla')
        self.assertRaises(ValidationError, MetadataBlock, buffer=-1)

    def test_stride(self):
        # test default stride
        metadata = MetadataBlock()
        self.assertEqual(1, metadata.stride)

        # test specified stride
        metadata = MetadataBlock(stride=2)
        self.assertEqual(2, metadata.stride)

        # test bad stride
        self.assertRaises(FieldTypeError, MetadataBlock, stride='1')
        self.assertRaises(ValidationError, MetadataBlock, stride=3)

    def test_format(self):
        # test default format
        metadata = MetadataBlock()
        self.assertEqual('png', metadata.format)

        # test specified format
        metadata = MetadataBlock(format='jpeg')
        self.assertEqual('jpeg', metadata.format)

        # test bad format
        self.assertRaises(FieldTypeError, MetadataBlock, format=1)
        self.assertRaises(ValidationError, MetadataBlock, format='abc')

    def test_format_options(self):
        # test default format options
        metadata = MetadataBlock()
        self.assertEqual(dict(), metadata.format_options)

        # test specified format options
        metadata = MetadataBlock(format_options=dict(quality=85))
        self.assertEqual(dict(quality=85), metadata.format_options)

        # test bad format options
        self.assertRaises(FieldTypeError, MetadataBlock, format_options=1)
        self.assertRaises(FieldTypeError, MetadataBlock, format_options='1')

    def test_attribution(self):
        # test default attribution
        metadata = MetadataBlock()
        self.assertEqual('', metadata.attribution)

        # test specified attribution
        metadata = MetadataBlock(attribution='copyright@stonemason')
        self.assertEqual('copyright@stonemason', metadata.attribution)

        # test bad attribution
        self.assertRaises(FieldTypeError, MetadataBlock, attribution=1)

    def test_to_json(self):
        metadata = MetadataBlock()

        expected = {
            "crs": "EPSG:3857",
            "scale": [1],
            "attribution": "",
            "name": "default",
            "format": "png",
            "buffer": 0,
            "format_options": dict(),
            "stride": 1
        }

        self.assertDictEqual(expected, json.loads(metadata.to_json()))

    def test_repr(self):
        metadata = MetadataBlock()

        expected = "MetadataBlock(name='default', crs='EPSG:3857', " \
                   "scale=[1], buffer=0, stride=1, format='png', " \
                   "format_options={}, attribution='')"

        self.assertEqual(expected, repr(metadata))


class TestModeBlock(unittest.TestCase):
    def test_mode(self):
        # test default values
        mode = ModeBlock()
        self.assertEqual(ModeBlock.MODE_STORAGE_ONLY, mode.mode)

        mode = ModeBlock(mode=ModeBlock.MODE_HYBRID)
        self.assertEqual(ModeBlock.MODE_HYBRID, mode.mode)

        # test bad values
        self.assertRaises(FieldTypeError, ModeBlock, mode=1)

    def test_to_json(self):
        mode = ModeBlock()

        expected = {
            "mode": "storage-only"
        }

        self.assertDictEqual(expected, json.loads(mode.to_json()))

    def test_repr(self):
        mode = ModeBlock()

        expected = "ModeBlock(mode='storage-only')"

        self.assertEqual(expected, repr(mode))



