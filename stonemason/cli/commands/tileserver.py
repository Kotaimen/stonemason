# -*- encoding: utf-8 -*-


"""
    stonemason.cli.commands.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Frontend tile server.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import multiprocessing

import click
import gunicorn.app.base
import six

from stonemason.service.tileserver import TileServerApp

from ..main import cli
from ..context import pass_context, Context

class TileServer(gunicorn.app.base.BaseApplication):
    """Integrated gunicorn application server"""

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


@cli.command('tileserver', short_help='frontend tile server.')
@click.option('-b', '--bind', default='127.0.0.1:7086', type=str,
              help='address and port to bind to.')
@click.option('-w', '--workers', default=0, type=click.IntRange(0, None),
              envvar='STONEMASON_WORKERS',
              help='''number of worker processes, default is cpu_num * 2.
              Read from envvar STONEMASON_WORKERS.''')
@click.option('--threads', default=1, type=click.IntRange(1, None),
              envvar='STONEMASON_THREADS',
              help='''number of threads per process, default is 1.
              Read from envvar STONEMASON_WORKERS.  ''')
@click.option('--cache', default=None, type=str,
              envvar='STONEMASON_CACHE',
              help='''tile cache configuration, default is None, which
              means caching is disabled.  Memcache hosts format is:
              host1:port1;host2:port2.
              Read from envvar STONEMASON_CACHE.
              ''')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode.', )
@pass_context
def tile_server_command(ctx, bind, read_only, workers, threads, cache):
    """Starts tile server using given themes configuration.

    Debug option:

    \b
        none    start a embedded gunicorn server,
        -d      enable debugging mode of the flask framework,
        -dd     use flask debugging server instead of gunicorn, suppots
                dynamic reloading.

    For production environments, a nginx server is also recommended, see
    gunicorn deployment guide for detailed instructions.

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
        'STONEMASON_CACHE': cache,
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
            'errorlog': '-',  # log to stderr
            'preload_app': False
        }
        server = TileServer(app, options)
        server.run()
