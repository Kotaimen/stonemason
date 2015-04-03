# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/2/15'

import unittest
import os

from click.testing import CliRunner

from stonemason.cli import cli


class TestStonemasonTileServer(unittest.TestCase):
    def test_export_wsgi(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)

            result = runner.invoke(cli, ['-dd', 'tileserver', '--write-wsgi',
                                         'application.py'])
            self.assertTrue(os.path.exists('application.py'))
            self.assertEqual(result.exit_code, 0)

    def test_dryrun_flask(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)

            result = runner.invoke(cli, ['-dd', 'tileserver', '--dry-run', ])
            self.assertEqual(result.exit_code, 0)

    def test_dryrun_gunicorn(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init'])
            self.assertEqual(result.exit_code, 0)

            result = runner.invoke(cli, ['-v', 'tileserver', '--dry-run', ])
            self.assertEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
