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
@click.option('-g', '--gallery',
              type=click.Path(exists=False, file_okay=False,
                              readable=True, resolve_path=True),
              required=False, default='map_gallery',
              help='''gallery root, by default, it looks "map_gallery" under
              current directory.  This option also can be specified
              using envvar STONEMASON_GALLERY.''')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, gallery):
    """Stonemason Tile Map Toolkit.

    Create, manage, render and serve map tiles.
    First initialize a gallery root using the "init" command:

        stonemason init

    Get help of each commands using:

        stonemason COMMAND --help
    """
    ctx.obj = Context()
    ctx.obj.gallery = os.path.abspath(gallery)
    if verbose > 0:
        click.secho('Gallery: %s' % ctx.obj.gallery, fg='green')
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug
