# -*- encoding: utf-8 -*-


"""
    stonemason.cli.commands.init
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Init a new theme root.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import click
import os
import shutil

from ..main import cli
from ..context import pass_context


@cli.command('init', short_help='init themes root.')
@pass_context
def init_theme_root_command(ctx):
    """Create a sample theme root directory."""
    if os.path.exists(ctx.themes):
        click.secho('Theme root already exists at %s.' % ctx.themes, err=True)
        raise click.Abort

    sample_dir = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir,
                                               'mason', 'theme', 'samples'))
    shutil.copytree(sample_dir, ctx.themes, symlinks=False)
    click.echo('Initialization complete, start a tile server using:')
    click.echo('    export STONEMASON_THEMES=%s' % ctx.themes)
    click.echo('    stonemason -dd tileserver')
