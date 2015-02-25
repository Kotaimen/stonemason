# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/23/15'

import unittest

from stonemason.mason.theme.element import ThemeElement


class TestThemeElement(unittest.TestCase):
    def setUp(self):
        self.root = ThemeElement(name='test', test_attr=1)

    def test_name(self):
        self.assertEqual('test', self.root.name)

    def test_attributes(self):
        self.assertEqual(1, self.root.attributes['test_attr'])

    def test_put_get_element(self):
        sub1 = ThemeElement(name='sub1', attr1=1)
        sub2 = ThemeElement(name='sub2', attr1=2)

        self.root.put_element(sub1.name, sub1)
        self.root.put_element(sub2.name, sub2)

        sub = self.root.get_element(sub1.name)
        self.assertEqual(sub, sub1)

        sub = self.root.get_element(sub2.name)
        self.assertEqual(sub, sub2)

    def test_has_element(self):
        sub = ThemeElement(name='sub')
        self.root.put_element(sub.name, sub)
        self.assertTrue(self.root.has_element(sub.name))

    def test_repr(self):
        self.assertEqual(
            'ThemeElement(name=test, test_attr=1)', repr(self.root))
