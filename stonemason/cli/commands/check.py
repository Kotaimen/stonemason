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
from stonemason.mason.theme import MemThemeManager, LocalThemeLoader


@cli.command('check', short_help='check theme configuration.')
@pass_context
def check_command(ctx):
    """Check whether the theme configuration is valid without start the server.
    """
    click.echo('Checking themes configuration at %s...' % ctx.themes)

    if not os.path.exists(ctx.themes):
        raise click.Abort()

    manager = MemThemeManager()
    loader = LocalThemeLoader(ctx.themes)
    loader.load_into(manager)

    mason = Mason()
    for theme_name in manager:
        theme = manager.get(theme_name)
        if ctx.verbose > 0:
            click.secho('name="%s"' % theme.name, fg='green')
            click.secho('\t%r' % theme.metadata, fg='green')
            click.secho('\t%r' % theme.pyramid, fg='green')
            click.secho('\t%r' % theme.maptype, fg='green')
            click.secho('\t%r' % theme.tileformat, fg='green')
            click.secho('\t%r' % theme.storage, fg='green')
            click.secho('\t%r' % theme.renderer, fg='green')
        mason.load_map_from_theme(theme)

    click.echo('Check completed.')
