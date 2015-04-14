# -*- encoding: utf-8 -*-

"""
    stonemason.cli.commands.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Check themes configuration.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import pprint
import os
import click

from ..main import cli
from ..context import pass_context, Context

from stonemason.mason import Mason
from stonemason.mason.theme import MemGallery, FileSystemCurator


@cli.command('check', short_help='check gallery configuration.')
@pass_context
def check_command(ctx):
    """Check whether the gallery configuration is valid without start
    tile server or rendering.
    """
    click.echo('Checking configuration at %s...' % ctx.gallery)

    if not os.path.exists(ctx.gallery):
        raise click.Abort()

    gallery = MemGallery()
    loader = FileSystemCurator(ctx.gallery)
    loader.add_to(gallery)

    mason = Mason()
    for theme_name in gallery:
        theme = gallery.get(theme_name)
        mason.load_portrayal_from_theme(theme)

        protrayal = mason.get_portrayal(theme_name)

        click.echo('Theme: %s' % protrayal.name)
        if ctx.verbose:
            click.secho('\t%s' % repr(protrayal.bundle), fg='green')
            click.secho('\t%s' % repr(protrayal.metadata), fg='green')
            click.secho('\t%s' % repr(protrayal.pyramid), fg='green')

        for n, m in enumerate(theme.tilematrix_set):
            click.echo('\tSchema: %s %s' % (protrayal.name, m.tag))
            if ctx.verbose:
                click.secho('\t\tmaptype=%s' % repr(m.maptype), fg='green')
                click.secho('\t\ttileformat=%s' % repr(m.tileformat), fg='green')
                click.secho('\t\tpyramid=%s' % repr(m.pyramid), fg='green')
                click.secho('\t\tstorage=%s' % repr(m.storage), fg='green')
                click.secho('\t\trenderer=%s' % repr(m.renderer), fg='green')

    click.echo('Check completed.')
