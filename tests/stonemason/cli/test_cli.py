# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/2/15'

import unittest
import os

import click
from click.testing import CliRunner

from stonemason.cli import cli
from tests import skipUnlessHasMapnik


class TestStonemasonCLI(unittest.TestCase):
    def test_main(self):
        runner = CliRunner()
        result = runner.invoke(cli, [])
        self.assertEqual(result.exit_code, 0)

    @skipUnlessHasMapnik()
    def test_check_command(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['--themes=themes_', '-v', 'check'], )
            self.assertNotEqual(result.exit_code, 0)

            result = runner.invoke(cli, ['--themes=themes_', 'init'])
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.exists('themes_'))

            result = runner.invoke(cli, ['init'],
                                   env={'STONEMASON_THEMES': 'themes_'})
            self.assertNotEqual(result.exit_code, 0)

            result = runner.invoke(cli, ['--themes=themes_', '-v', 'check'], )
            self.assertEqual(result.exit_code, 0)

            # def test_tileserver_command(self):
            # runner = CliRunner()
            #     with runner.isolated_filesystem():
            #         result = runner.invoke(cli, ['init'])
            #         self.assertEqual(result.exit_code, 0)
            #
            #         result = runner.invoke(cli, ['-dd', 'tileserver'])
            #         self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
