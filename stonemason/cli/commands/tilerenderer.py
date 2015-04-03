# -*- encoding: utf-8 -*-

"""
    stonemason.cli.commands.tilerenderer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Simple tile renderer.
"""

__author__ = 'kotaimen'
__date__ = '3/31/15'

import os
import re

import click

from stonemason.mason import Mason
from stonemason.mason.theme import MemThemeManager, LocalThemeLoader

from ..main import cli
from ..context import pass_context, Context


def parse_levels(ctx, param, value):
    if value is None:
        return None

    levels = []
    for level in value.split(','):
        if re.match(r'^\d+$', level):
            levels.append(int(level))
        elif re.match(r'^\d+-\d+$', level):
            start, end = tuple(map(int, level.split('-')))
            for l in range(start, end + 1):
                levels.append(l)
        else:
            raise click.BadParameter('must be a list of integers or ranges.')
    return sorted(set(levels))


@cli.command('tilerenderer', short_help='single node tile renderer.')
@click.option('-w', '--workers', default=0, type=click.IntRange(0, None),
              help='''number of render worker processes, default is number of
              cpu cores.''')
@click.option('-l', '--levels', default=None, type=str, callback=parse_levels,
              help='''specify layers to render (eg:5,6,7 or 2-10), by default,
              levels defined in map theme is used.''')
@click.option('-e', '--envelope', default=None, nargs=4, type=float,
              help='''area to render specified as a envelope [left,bottom,right,top],
              in geography coordinate system.  By default, envelope defined
              in map theme is used.''')
@click.option('-c', '--csv', default=None,
              type=click.Path(dir_okay=False, exists=True),
              help='''render according to given CSV tile index list.''')
@click.argument('theme_name', type=str)
@pass_context
def tile_renderer_command(ctx, theme_name, workers, levels, envelope, csv):
    """Start a tile rendering process on this node.

    Specify name of the theme to render, then either use levels and envelope,
    or a render list csv file to set render areas.
    """
    assert isinstance(ctx, Context)

    # manager = MemThemeManager()
    # loader = LocalThemeLoader(ctx.themes)
    # loader.load_into(manager)
    #
    # mason = Mason()
    # mason.load_theme(manager.get(theme_name))
    #
    # if ctx.verbose:
    # click.secho('Rendering theme "%s"' % theme_name, fg='green')
    #     click.secho('Using %d' % workers, fg='green')

