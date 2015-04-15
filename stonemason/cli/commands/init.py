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


@cli.command('init', short_help='init a gallery with sample theme.')
@pass_context
def init_theme_root_command(ctx):
    """Create a new map gallery with a sample theme."""
    if os.path.exists(ctx.gallery):
        click.secho('Gallery already exists at %s.' % ctx.gallery, err=True)
        raise click.Abort

    sample_dir = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                               os.pardir, os.pardir,
                                               'mason', 'theme', 'samples'))
    shutil.copytree(sample_dir, ctx.gallery, symlinks=False)
    click.echo('Initialization complete, start a tile server using:')
    click.echo('\texport STONEMASON_GALLERY=%s' % ctx.gallery)
    click.echo('\tstonemason -dd tileserver')
    click.echo('Or check configuration using:')
    click.echo('\tstonemason --gallery=%s check' % ctx.gallery)
