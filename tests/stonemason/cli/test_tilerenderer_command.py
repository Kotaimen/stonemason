# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/2/15'

import unittest
import os

import click
from click.testing import CliRunner

from stonemason.cli import cli
from stonemason.cli.commands.tilerenderer import parse_levels

from tests import skipUnlessHasMapnik


class TestHelpers(unittest.TestCase):
    def test_parse_levels(self):
        self.assertListEqual(
            parse_levels(None, None, '1'),
            [1]
        )
        self.assertListEqual(
            parse_levels(None, None, '1,3,5'),
            [1, 3, 5]
        )
        self.assertListEqual(
            parse_levels(None, None, '2-6'),
            [2, 3, 4, 5, 6]
        )
        self.assertListEqual(
            parse_levels(None, None, '1,3,6-9'),
            [1, 3, 6, 7, 8, 9]
        )
        self.assertListEqual(
            parse_levels(None, None, '3,1,3,10-9,3-5'),
            [1, 3, 4, 5]
        )
        self.assertRaises(click.BadParameter,
                          parse_levels,
                          None, None, '1,a')

@skipUnlessHasMapnik()
class TestStonemasonTileRenderer(unittest.TestCase):
    def test_tilerender(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)

            result = runner.invoke(cli, [
                '-v',
                'tilerenderer', 'sample_world',
                '--workers=2', '--levels=2-4',
                '--envelope',
                '0', '-80', '180', '80'])
            self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
