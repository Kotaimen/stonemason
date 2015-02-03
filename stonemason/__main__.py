#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/3/15'

import sys
import click

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='STONEMASON',
    help_option_names=['-h', '--help'],
)


class Context(object):
    def __init__(self):
        self.themes = None
        self.verbose = False
        self.debug = False


pass_context = click.make_pass_decorator(Context)

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
    ctx.obj.themes = themes
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug


from stonemason.service.tileserver import TileServerApp


@cli.command('tileserver', short_help='frontend tile server.')
@click.option('-b', '--bind', default='127.0.0.1:7086', type=str,
              help='address and port to bind to')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode', )
@pass_context
def tile_server(ctx, bind, read_only):
    """Starts tile server using given themes root."""
    if read_only:
        click.secho('Starting tileserver in read only mode.', fg='red')
    host, port = bind.split(':')
    port = int(port)
    app = TileServerApp(themes=ctx.themes,
                        read_only=read_only)
    app.run(host=host, port=port)


if __name__ == '__main__':
    cli()
