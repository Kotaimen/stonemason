# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver.app
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements the tile server app for Stonemason.

"""

import os
from logging import StreamHandler, Formatter

import six
from werkzeug.http import http_date
from flask import Flask, render_template, abort, make_response
from flask.views import MethodView
from flask.json import jsonify

from stonemason.mason import Mason

from . import default_settings


class ThemeAPI(MethodView):
    """ Theme Resource API

    Retrieve theme information with a given theme tag. If tag is not provided,
    return a list of available themes. Raise Htt

    :type mason: :class:`~stonemason.mason.Mason`
    :param mason:

        A mason instance that contains available themes.

    """

    def __init__(self, mason):
        MethodView.__init__(self)
        self._mason = mason

    def get(self, tag):
        """Return a theme info and raise :http:statuscode:`404` when theme is
        not available.

        :type tag: str
        :param tag:

            The Name of a theme. A string literal that uniquely identify a
            theme.
            
        """
        if tag is None:
            themes = self._mason.themes()
            return jsonify(result=themes)
        else:
            theme = self._mason.get_theme(tag)
            return jsonify(result=theme)


class TileAPI(MethodView):
    """ Tile Resource API

    Get Tile with a tag, zoom level and (x, y) coordinates. Raise
    :http:statuscode:`400` when request is not valid.


    :type mason: :class:`~stonemason.mason.Mason`
    :param mason:

        A mason instance that contains available themes.

    """

    def __init__(self, mason):
        MethodView.__init__(self)
        self._mason = mason

    def get(self, tag, z, x, y, scale, ext):
        """Return a tile data and raise :http:statuscode:`404` when tile is
        not available.

        :type tag: str
        :param tag:

            The Name of a theme. A string literal that uniquely identify a
            theme.

        :type z: int
        :param z:

            A positive integer that represents the zoom level of a tile.

        :type x: int
        :param x:

            A positive integer that represents the coordinate along x axis. A
            valid would be 0 to :math:`2^z - 1`.

        :type y: int
        :param y:

            A positive integer that represents the coordinate along y axis. A
            valid would be 0 to :math:`2^z - 1`.

        :type scale: str
        :param scale:

            A positive integer that scales elements like font, stroke during
            rendering process for display on high resolution device.

        :type ext: str
        :param ext:

            A string literal that indicates the output format of the requested
            tile.

        """
        tile = self._mason.get_tile(tag, z, x, y, scale, ext)
        if tile is None:
            abort(404)

        response = make_response(tile.data)

        # set response headers
        response.headers['Content-Type'] = tile.mimetype
        response.headers['ETag'] = tile.etag
        response.headers['Last-Modified'] = http_date(tile.mtime)
        response.headers['Cache-Control'] = 'public, max-age=86400'

        return response


class MapAPI(MethodView):
    def __init__(self, mason):
        MethodView.__init__(self)
        self._mason = mason

    def get(self, tag):
        return render_template('map.html', theme=self._mason.get_theme(tag))


class Home(MethodView):
    def __init__(self, mason):
        MethodView.__init__(self)
        self._mason = mason

    def get(self):
        return render_template('index.html', themes=self._mason.themes())


def health_check():
    response = make_response()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


class TileServerApp(Flask):
    """StoneMason tile server application.

    Implements the tile map frontend service, also acting as a debugging
    all-in-one server.

    Configuration is loaded in the following order, each overwriting the
    previous ones:

        1. :class:`stonemason.service.tileserver.default_settings`,
        2. Configuration file,
        3. Environment variables.
        4. Command line options.

    Tile server exposes following REST API:

        :http:get:`/themes`

        :http:get:`/themes/(tag)`

        :http:get:`/tiles/(tag)/(int:z)/(int:x)/(int:y)@(scale).(ext)`

        :http:get:`/tiles/(tag)/(int:z)/(int:x)/(int:y).(ext)`

    With a management interface at site root:

        :http:get:`/`

    :type config: str
    :param config:

        Path of configuration file on your system.

    :type kwargs: dict
    :param kwargs:

        Extra configurations specified on the creation of ``TileServerApp``.
        Used to accept variables from command line options.

        The following parameters are available now:

        - STONEMASON_THEMES:

            The directory path of the themes.

        - STONEMASON_DEBUG:

            Turn on debug mode. True or False.

        - STONEMASON_VERBOSE:

            Print verbose logs. 1 or 0.

        - STONEMASON_MEMCACHE_SERVERS:

            Specify memcache servers. A list of servers.
    """

    ENV_PARAM_PREFIX = 'STONEMASON_'

    def __init__(self, config=None, **kwargs):
        package_root = os.path.dirname(__file__)
        Flask.__init__(self, self.__class__.__name__,
                       template_folder=os.path.join(package_root, 'templates'),
                       static_folder=os.path.join(package_root, 'static'),
                       instance_relative_config=True)

        # load configs and parameters
        self._load_config(config, **kwargs)

        # initialize mason
        self._mason = Mason()

        # load themes
        theme_dir = self.config.get('STONEMASON_THEMES')
        self._mason.load_theme_from_directory(theme_dir)

        # A list of available maps
        self.add_url_rule(rule='/',
                          view_func=Home.as_view('home', self._mason),
                          methods=['GET'])

        # health check
        self.add_url_rule(rule='/health_check',
                          view_func=health_check,
                          methods=['GET'])

        map_view = MapAPI.as_view('map_api', self._mason)
        self.add_url_rule(
            rule='/maps/<tag>',
            view_func=map_view,
            methods=['GET']
        )

        # TODO: Move APIs to a separate BluePrint
        theme_view = ThemeAPI.as_view('theme_api', self._mason)
        self.add_url_rule(
            rule='/themes',
            defaults={'tag': None},
            view_func=theme_view,
            methods=['GET']
        )
        self.add_url_rule(
            rule='/themes/<tag>',
            view_func=theme_view,
            methods=['GET']
        )

        tile_view = TileAPI.as_view('tile_api', self._mason)
        self.add_url_rule(
            rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>@<scale>.<ext>',
            view_func=tile_view,
            methods=['GET']
        )
        self.add_url_rule(
            rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>.<ext>',
            defaults={'scale': '1x'},
            view_func=tile_view,
            methods=['GET']
        )

    def _load_config(self, config, **kwargs):
        # config from default values
        self.config.from_object(default_settings)

        # config from setting file
        if config is not None:
            self.config.from_pyfile(config, silent=True)


        # config from environment variables
        for key, val in six.iteritems(os.environ):
            if key.startswith(self.ENV_PARAM_PREFIX):
                self.config[key] = val

        # config from command-line options
        self.config.update(kwargs)

        # log debug info
        if self.config.get('STONEMASON_DEBUG'):
            self.config['DEBUG'] = True

        if self.config.get('STONEMASON_VERBOSE') is not None:
            try:
                verbosity = int(self.config['STONEMASON_VERBOSE'])
            except ValueError:
                verbosity = 0

            # create a log handler for none debug use
            if verbosity > 0:
                class VerboseHandler(StreamHandler):
                    def emit(x, record):
                        StreamHandler.emit(x, record)

                handler = VerboseHandler()
                handler.setLevel('INFO')
                handler.setFormatter(Formatter(self.debug_log_format))

                self.logger.addHandler(handler)
                self.logger.setLevel('INFO')

        if config is not None:
            self.logger.info('LOADED CONFIG: filename=%s' %
                             os.path.join(self.instance_path, config))

        for key, val in six.iteritems(os.environ):
            if key.startswith(self.ENV_PARAM_PREFIX):
                self.logger.info('LOADED ENV PARAM: %s=%s' % (key, val))

        for key, val in six.iteritems(kwargs):
            self.logger.info('Loading CMD PARAM: %s=%s' % (key, val))
