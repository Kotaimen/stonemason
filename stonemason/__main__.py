#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Main CLI entry point, using Click as argument parser."""

__author__ = 'kotaimen'
__date__ = '2/3/15'

import os
import sys
import multiprocessing

import click
import six

import gunicorn.app.base

#
# Click contexts
#

# NOTE: click add "_" between prefix and variable, but Flask don't...
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
# Gunicorn based standalone server
#

class TileServer(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(TileServer, self).__init__()

    def load_config(self):
        config = dict(
            [(key, value) for key, value in six.iteritems(self.options)
             if key in self.cfg.settings and value is not None])
        for key, value in six.iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

#
# Main entry
#
import stonemason


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', default=False, help='debug mode.')
@click.option('-v', '--verbose', default=False, count=True,
              help='being verbose.')
@click.option('-t', '--themes', type=click.Path(exists=False), required=True,
              help='themes root directory, can be overridden using envvar '
                   'STONEMASON_THEMES.')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, themes):
    """Stonemason Tile Map Service Toolkit."""
    ctx.obj = Context()
    ctx.obj.themes = os.path.abspath(themes)
    ctx.obj.verbosity = verbose
    ctx.obj.debug = debug

#
# Tile Server Command
#
from stonemason.service.tileserver import TileServerApp


@cli.command('tileserver', short_help='frontend tile server.')
@click.option('-b', '--bind', default='127.0.0.1:7086', type=str,
              help='address and port to bind to')
@click.option('-w', '--workers', default=0, type=click.IntRange(0, None),
              help='number of worker processes, default is cpu_num * 2')
@click.option('--threads', default=1, type=click.IntRange(1, None),
              help='number of worker threads per process, default is 1')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode', )
@pass_context
def tile_server(ctx, bind, read_only, workers, threads):
    """Starts tile server using given themes root."""
    assert isinstance(ctx, Context)

    if read_only and ctx.verbosity > 0:
        click.secho('Starting tileserver in read only mode.', fg='red')

    # parse binding port
    host, port = bind.split(':')
    port = int(port)

    app_config = {
        'THEMES': ctx.themes,
        'READ_ONLY': read_only,
        'DEBUG': ctx.debug,
        'VERBOSITY': ctx.verbosity
    }
    # add prefix to all config keys to confront with flask config
    app_config = dict((ENVVAR_PREFIX + '_' + k, v)
                      for (k, v) in six.iteritems(app_config))

    # Flask based WSGI application
    app = TileServerApp(**app_config)

    if ctx.debug:
        # run Flask server in debug mode
        app.run(host=host, port=port, debug=ctx.debug)
    else:
        # otherwise, start gunicorn server
        if workers == 0:
            workers = multiprocessing.cpu_count() * 2
        options = dict(
            workers=workers,
            threads=threads,
            bind=bind,
        )
        server = TileServer(app, options)
        server.run()


#
# Theme Root Init Command
#
@cli.command('init', short_help='init themes root.')
@pass_context
def init_theme(ctx, sample):
    click.secho('Initializing themes root at %s...' % ctx.themes)
    # TODO: Init theme root


#
# Theme Root Init Command
#
@cli.command('check', short_help='check theme configuration.')
@pass_context
def check_config(ctx, sample):
    click.secho('Checking themes configuration at %s...' % ctx.themes)
    # TODO: Check config


if __name__ == '__main__':
    cli()

