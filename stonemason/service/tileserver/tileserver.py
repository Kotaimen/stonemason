# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver.app
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the tile server app for Stonemason.

"""

import os

import six
from flask import Flask, render_template
from flask.views import View, MethodView
from flask.json import jsonify

from . import default_settings

from stonemason.mason import Mason


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
            themes = self._mason.get_themes()
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
        return self._mason.get_tile(tag, z, x, y, scale, ext)


def home():
    import stonemason
    return render_template('index.html', version=stonemason.__version__)


class TileServerApp(Flask):
    """StoneMason tile server application.

    Implements the tile map frontend service, also acting as a debugging
    all-in-one server.

    Configuration is loaded in the following order, each overwriting the
    previous ones:
        1. :class:`stonemason.service.tileserver.default_settings`,
        2. Configuration file,
        3. Environment variables.

    Tile server exposes following REST API:

        :http:get:`/themes`

        :http:get:`/themes/(tag)`

        :http:get:`/tiles/(tag)/(int:z)/(int:x)/(int:y)@(scale).(ext)`

        :http:get:`/tiles/(tag)/(int:z)/(int:x)/(int:y).(ext)`

    With a management interface at site root:

        :http:get:`/`

    """

    ENV_PARAM_PREFIX = 'STONEMASON_'

    def __init__(self, config=None):
        package_root = os.path.dirname(__file__)
        Flask.__init__(self, self.__class__.__name__,
                       template_folder=os.path.join(package_root, 'templates'),
                       static_folder=os.path.join(package_root, 'static'),
                       instance_relative_config=True)

        self._load_config(config)

        self._mason = Mason()

        # XXX: Just a sample index page
        self.add_url_rule(rule='/',
                          view_func=home,
                          methods=['GET'])

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
            rule='/tile/<tag>/<int:z>/<int:x>/<int:y>@<scale>.<ext>',
            view_func=tile_view,
            methods=['GET']
        )
        self.add_url_rule(
            rule='/tile/<tag>/<int:z>/<int:x>/<int:y>.<ext>',
            defaults={'scale': '1x'},
            view_func=tile_view,
            methods=['GET']
        )

    def _load_config(self, config):
        # config from default values
        self.config.from_object(default_settings)

        # config from setting file
        if config is not None:
            self.config.from_pyfile(config, silent=True)

        # config from environment variables
        for key, val in six.iteritems(os.environ):
            if key.startswith(self.ENV_PARAM_PREFIX):
                self.config[key] = val
