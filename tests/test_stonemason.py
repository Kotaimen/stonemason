# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '12/26/14'

import unittest
from distutils.version import LooseVersion

import stonemason


class TestStonemason(unittest.TestCase):
    def test_something(self):
        self.assertGreaterEqual(LooseVersion(stonemason.__version__),
                                LooseVersion('0'))


if __name__ == '__main__':
    unittest.main()
