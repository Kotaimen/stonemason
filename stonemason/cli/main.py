# -*- encoding: utf-8 -*-

"""
    stonemason.cli.main
    ~~~~~~~~~~~~~~~~~~~

    CLI main command.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import os

import click
import stonemason

from .context import CONTEXT_SETTINGS, Context


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--debug', default=False, count=True,
              help='''enable debug mode, this option can be specified several
              times.''')
@click.option('-v', '--verbose', default=False, count=True,
              help='being verbose.')
@click.option('-t', '--themes',
              type=click.Path(exists=False, file_okay=False,
                              readable=True, resolve_path=True),
              required=False, default='themes',
              help='''themes root, by default, it looks "themes" under
              current directory.  This option also can be specified
              using envvar STONEMASON_THEMES.''')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, themes):
    """Stonemason Tile Map Toolkit.

    Create, manage, render and serve map tiles.
    First initialize a themes root using the "init" command:

        stonemason init

    Get help of each commands using:

        stonemason COMMAND --help
    """
    ctx.obj = Context()
    ctx.obj.themes = os.path.abspath(themes)
    if verbose > 0:
        click.secho('Themes root: %s' % ctx.obj.themes, fg='green')
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
