#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Main CLI entry point, using Click as argparser."""

__author__ = 'kotaimen'
__date__ = '2/3/15'

import os
import shutil
import multiprocessing
import sys

import click
import six

import gunicorn.app.base


# HACK: Fix import error when debug is true when using Flask reloading
if sys.argv[0].endswith('__main__.py'):
    sys.path.insert(0, os.path.abspath(
        os.path.join(__file__, os.path.pardir, os.path.pardir)))

#
# Click contexts
#

# NOTE: Click adds "_" between prefix and variable, but Flask doesn't...
ENVVAR_PREFIX = 'STONEMASON'

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix=ENVVAR_PREFIX,
    help_option_names=['-h', '--help'],
)


class Context(object):
    """Custom context object, collecting options from group command,
    and pass them to sub commands."""

    def __init__(self):
        self.themes = None
        self.verbose = 0
        self.debug = 0


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
        # TODO: Also supports Gunicorn configuration files
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
@click.option('-d', '--debug', default=False, count=True,
              help='''enable debug mode, this option can be specified several
              times:
                -d      enable debugging mode of the flask framework,
                -dd     use flask debugging server instead of gunicorn.
              ''')
@click.option('-v', '--verbose', default=False, count=True,
              help='being verbose.')
@click.option('-t', '--themes',
              type=click.Path(exists=False, file_okay=True,
                              readable=True),
              required=False, default='themes',
              help='''themes root directory, by default, it looks "themes"
              under current directory, note the directory must already exists.
              Read from envvar STONEMASON_THEMES.''')
@click.version_option(stonemason.__version__, message='Stonemason %(version)s')
@click.pass_context
def cli(ctx, debug, verbose, themes):
    """Stonemason Tile Map Service Toolkit."""
    ctx.obj = Context()
    ctx.obj.themes = os.path.abspath(themes)
    if verbose > 0:
        click.secho('Themes root: %s' % ctx.obj.themes, fg='green')
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug

#
# Tile Server Command
#
from stonemason.service.tileserver import TileServerApp


@cli.command('tileserver', short_help='frontend tile server.')
@click.option('-b', '--bind', default='127.0.0.1:7086', type=str,
              help='address and port to bind to.')
@click.option('-w', '--workers', default=0, type=click.IntRange(0, None),
              envvar='STONEMASON_WORKERS',
              help='''number of worker processes, default is cpu_num * 2,
              Read from envvar STONEMASON_WORKERS.''')
@click.option('--threads', default=1, type=click.IntRange(1, None),
              envvar='STONEMASON_THREADS',
              help='''number of worker threads per process, default is 1.
              Read from envvar STONEMASON_WORKERS.  ''')
@click.option('--cache', default=None, type=str,
              envvar='STONEMASON_MEMCACHE_HOSTS',
              help='''tile cache configuration, default is None, which
              means caching is disabled.  Memcache hosts format is:
              host1:port1;host2:port2.
              Read from envvar STONEMASON_MEMCACHE_HOSTS.
              ''')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode.', )
@pass_context
def tile_server(ctx, bind, read_only, workers, threads, cache):
    """Starts tile server using given themes configuration.

    When debug mode>2, a flask debugging server is used.  Otherwise, gunicorn
    is used as http server.  A nginx is also recommended for any internet facing
    services.

    Note for python2, threading mode maybe not available unless `futures`
    package is installed.

    By default, tile cache is not enabled, to connect to a default configured
    local memcache server, use --cache=localhost:11211.
    """
    assert isinstance(ctx, Context)

    if read_only and ctx.verbose > 0:
        click.secho('Tile server started in read only mode.', fg='green')

    # parse binding port
    host, port = bind.split(':')
    port = int(port)

    app_config = {
        'STONEMASON_THEMES': ctx.themes,
        'STONEMASON_READ_ONLY': read_only,
        'STONEMASON_DEBUG': bool(ctx.debug),
        'STONEMASON_VERBOSE': ctx.verbose,
        'STONEMASON_MEMCACHE_HOSTS': cache,
    }

    # Flask based WSGI application
    app = TileServerApp(**app_config)

    if ctx.debug > 1:
        # run Flask server in debug mode
        if ctx.verbose:
            click.secho('Starting Flask debug tile server.', fg='green')
        app.run(host=host, port=port, debug=ctx.debug)
    else:
        # otherwise, start gunicorn server

        if workers == 0:
            # by default, use cpu num * 2
            workers = multiprocessing.cpu_count() * 2
        if ctx.verbose:
            click.secho(
                'Starting Gunicorn tile server using %d worker(s) ' \
                'and %d thread(s) per worker' % (workers, threads), fg='green')
            log_level = 'debug'
        else:
            log_level = 'info'

        options = {
            'workers': workers,
            'threads': threads,
            'bind': bind,
            'loglevel': log_level,
            'errorlog': '-',  # stderr
            'preload_app': False
        }
        server = TileServer(app, options)
        server.run()


#
# Theme Root Init Command
#
@cli.command('init', short_help='init themes root.')
@pass_context
def init_theme(ctx):
    """Create a sample theme root directory."""
    if os.path.exists(ctx.themes):
        click.secho('Theme root already exists at %s' % ctx.themes, err=True)
        return -1
    shutil.copytree(
        os.path.join(os.path.dirname(__file__), 'mason', 'theme', 'samples'),
        ctx.themes,
        symlinks=False)
    click.echo('Initialization complete, start a tile server using:')
    click.echo('    export STONEMASON_THEMES=%s' % ctx.themes)
    click.echo('    stonemason --debug tileserver')


#
# Theme Root Init Command
#
from stonemason.mason import Mason
from stonemason.mason.theme import DictThemeManager, DirectoryThemeLoader


@cli.command('check', short_help='check theme configuration.')
@pass_context
def check_config(ctx):
    """Check whether the theme configuration is valid without start the server.
    """
    click.secho('Checking themes configuration at %s...' % ctx.themes)

    manager = DictThemeManager()
    loader = DirectoryThemeLoader(ctx.themes)
    loader.load(manager)

    mason = Mason()
    for theme_name in manager.list():
        theme = manager.get(theme_name)
        mason.load_theme(theme)


if __name__ == '__main__':
    cli()

