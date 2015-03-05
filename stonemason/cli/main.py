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
              type=click.Path(exists=False, file_okay=True,
                              readable=True),
              required=False, default='themes',
              help='''themes root directory, by default, it looks "themes"
              under current directory, note the directory must already exists.
              Read from envvar STONEMASON_THEMES.''')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, themes):
    """Stonemason Tile Map Service Toolkit."""
    ctx.obj = Context()
    ctx.obj.themes = os.path.abspath(themes)
    if verbose > 0:
        click.secho('Themes root: %s' % ctx.obj.themes, fg='green')
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
