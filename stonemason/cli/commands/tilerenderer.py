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
import multiprocessing

import click

from stonemason.util.timer import Timer, human_duration
from stonemason.service.renderman import renderman, RenderScript, RenderStats

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
@click.option('--log', default='render.log', type=click.Path(dir_okay=False),
              help='''Specify a file name for render error logs, default
              value is "render.log"''')
@click.argument('theme_name', type=str)
@click.argument('schema_tag', type=str)
@pass_context
def tile_renderer_command(ctx, theme_name, schema_tag,
                          levels, envelope,
                          workers, csv, log):
    """Start a tile rendering process on this node.

    Specify name of the theme to render, then either use levels and envelope,
    or a render list csv file to set render areas.
    """
    assert isinstance(ctx, Context)

    if workers == 0:
        workers = multiprocessing.cpu_count()

    script = RenderScript(verbose=ctx.verbose,
                          debug=ctx.debug,
                          gallery=ctx.gallery,
                          theme_name=theme_name,
                          schema_tag=schema_tag,
                          levels=levels,
                          envelope=envelope,
                          csv_file=csv,
                          workers=workers,
                          log_file=log)
    timer = Timer()
    timer.tic()
    stat = renderman(script)
    timer.tac()

    click.secho('Succeeded MetaTiles : %d' % stat.rendered, fg='green')
    click.secho('   Failed MetaTiles : %d' % stat.failed, fg='green')
    click.secho('     Total CPU Time : %s' % human_duration(stat.total_time),
                fg='green')
    click.secho('         Time Taken : %s' % human_duration(timer.get_time()),
                fg='green')
    if stat.rendered > 0:
        click.secho('       Render Speed : %s/MetaTile' % \
                    human_duration(stat.total_time / stat.rendered),
                    fg='green')
