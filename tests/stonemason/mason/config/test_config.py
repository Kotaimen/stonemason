# -*- encoding: utf-8 -*-

import os
import unittest
from collections import namedtuple
from stonemason.mason.config import Config, FileNotFound, InvalidConfig
from tests import DATA_DIRECTORY


class TestConfig(unittest.TestCase):
    def test_read_from_file(self):
        filename = os.path.join(DATA_DIRECTORY, 'config', 'config.json')

        conf = Config()
        conf.read_from_file(filename)

        self.assertEqual(conf['name'], 'stonemason')

    def test_read_from_stream(self):
        filename = os.path.join(DATA_DIRECTORY, 'config', 'config.json')

        conf = Config()
        with open(filename, 'r') as fp:
            conf.read_from_stream(fp)

        self.assertEqual(conf['name'], 'stonemason')

    def test_read_from_object(self):
        Foo = namedtuple('Foo', 'name')
        obj = Foo('stonemason')

        conf = Config()
        conf.read_from_object(obj)

        self.assertEqual(conf['name'], 'stonemason')

    def test_read_from_dict(self):
        obj = dict(name='stonemason')
        conf = Config()
        conf.read_from_dict(obj)
        self.assertEqual(conf['name'], 'stonemason')

    def test_error_file_not_found(self):
        bad_filename = os.path.join(DATA_DIRECTORY, 'config', 'foo')

        conf = Config()
        self.assertRaises(FileNotFound, conf.read_from_file, bad_filename)

    def test_error_parse(self):
        filename = os.path.join(DATA_DIRECTORY, 'config', 'bad_config.json')

        conf = Config()
        self.assertRaises(InvalidConfig, conf.read_from_file, filename)
