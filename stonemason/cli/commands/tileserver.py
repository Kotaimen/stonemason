# -*- encoding: utf-8 -*-


"""
    stonemason.cli.commands.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Frontend tile server.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import multiprocessing
import pprint
import os

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


def write_wsgi_file(app_config, write_wsgi):
    with open(write_wsgi, 'w') as fp:
        fp.write('''#! -*- coding: ascii -*-
from stonemason.service.tileserver import TileServerApp
config = \
%s
application = TileServerApp(**config)
''' % pprint.pformat(app_config, indent=4))


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
@click.option('--max-age', default=300, type=int,
              envvar='STONEMASON_MAX_AGE',
              help='''Max-age of cache control header returned by tile api,
              default is 300. Set to 0 disables cache control header,
              which is the default behaviour when debugging
              tile server is used (specified by -dd option).''')
@click.option('--read-only', is_flag=True,
              help='start the server in read only mode.', )
@click.option('--write-wsgi',
              type=click.Path(dir_okay=False, resolve_path=True, writable=True),
              default=None,
              help='''Write a WSGI application file using current given
              configuration and exit.''')
@click.option('--dry-run', is_flag=True, default=False,
              help='''Create the server instance without running it,
              then exit.''')
@pass_context
def tile_server_command(ctx, bind, read_only, workers,
                        threads, cache, max_age,
                        write_wsgi, dry_run):
    """Starts tile server using given gallery configuration.

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

    # disable cache control when debugging
    if ctx.debug > 1:
        max_age = 0

    app_config = {
        'STONEMASON_GALLERY': ctx.gallery,
        'STONEMASON_READ_ONLY': read_only,
        'STONEMASON_DEBUG': bool(ctx.debug),
        'STONEMASON_VERBOSE': ctx.verbose,
        'STONEMASON_CACHE': cache,
        'STONEMASON_MAX_AGE': max_age,
    }

    # Flask based WSGI application
    app = TileServerApp(**app_config)

    # write wsgi file
    if write_wsgi:
        if ctx.verbose:
            click.secho('Writing WSGI application to %s' % write_wsgi,
                        fg='green')
        write_wsgi_file(app_config, write_wsgi)
        return 0

    elif ctx.debug > 1:
        # run in flask debug mude
        if ctx.verbose:
            click.secho('Starting Flask debug tile server.', fg='green')

        extra_files = list()
        for root, dirs, files in os.walk(ctx.gallery):
            if 'cache' in dirs:
                dirs.remove('cache')  # don't visit CVS directories
            for filename in files:
                if filename.endswith('.mason'):
                    extra_files.append(os.path.join(root, filename))
        if ctx.verbose:
                click.secho('Watching %d extra files.' % len(extra_files), fg='green')

        if not dry_run:
            app.run(host=host, port=port,
                    debug=ctx.debug,
                    extra_files=extra_files)

    else:
        # start a gunicorn server

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
        if not dry_run:
            server.run()
