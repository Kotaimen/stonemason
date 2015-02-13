#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Main CLI entry point, using Click as argument parser."""

__author__ = 'kotaimen'
__date__ = '2/3/15'

import sys
import os
import click
import six

# NOTE: click will add "_" between prefix and variable, but flask don't...
ENVVAR_PREFIX = 'STONEMASON'

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix=ENVVAR_PREFIX,
    help_option_names=['-h', '--help'],
)


class Context(object):
    """Custom context object, passing options collected from group command.
    """

    def __init__(self):
        self.themes = None
        self.verbosity = 0
        self.debug = False


pass_context = click.make_pass_decorator(Context)

#
# Main entry
#
import stonemason


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', default=False, help='debug mode.')
@click.option('-v', '--verbose', default=False, count=True,
              help='being verbose.')
@click.option('--themes', type=click.Path(exists=False), required=True,
              help='themes root directory, can be overridden using envvar '
                   'STONEMASON_THEMES.')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, themes):
    """Stonemason Tile Map Service Toolkit."""
    ctx.obj = Context()
    ctx.obj.themes = os.path.abspath(themes)
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug

#
# Tile Server Command
#
from stonemason.service.tileserver import TileServerApp


@cli.command('tileserver', short_help='frontend tile server.')
@click.option('-b', '--bind', default='127.0.0.1:7086', type=str,
              help='address and port to bind to')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode', )
@pass_context
def tile_server(ctx, bind, read_only):
    """Starts tile server using given themes root."""
    assert isinstance(ctx, Context)

    if read_only and ctx.verbose > 0:
        click.secho('Starting tileserver in read only mode.', fg='red')

    # parse binding port
    host, port = bind.split(':')
    port = int(port)

    config = {
        'THEMES': ctx.themes,
        'READ_ONLY': read_only,
        'DEBUG': ctx.debug,
        'VERBOSE': ctx.verbose
    }
    # add prefix to all config keys to confront with flask config
    config = dict((ENVVAR_PREFIX + '_' + k, v)
                  for (k, v) in six.iteritems(config))

    app = TileServerApp(**config)
    app.run(host=host, port=port,
            debug=ctx.debug)


#
# Theme Root Init Command
#
@cli.command('init', short_help='init themes root.')
@pass_context
def tile_server(ctx, sample):
    click.secho('Initializing themes root at %s...' % ctx.themes)
    # TODO: Init theme root


if __name__ == '__main__':
    cli()

