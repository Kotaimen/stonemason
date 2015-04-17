# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A high performance tile server WSGI application based on Flask.
"""

import re
import os

import six
from flask import Flask

from .models import ThemeModel, MasonModel
from . import themes
from . import maps
from . import health
from . import default_settings


class FlaskAppConfig(object):  # pragma: no cover
    """Base Flask App Config

    `FlaskAppConfig` is a helper class that serves to configures flask app
    in many different ways. Subclasses could implement details about how to
    setup app parameters from various sources.

    """

    def configure(self, app):
        """ Configures app parameters

        :type app: :class:`flask.Flask`
        :param app: A flask app instance.
        """
        raise NotImplementedError


class ObjectConfig(FlaskAppConfig):
    """Object Config

    `ObjectConfig` configures flask app from an object. The object could be
    either an actual object or a string.

    Objects are usually either modules or classes and in the case of string,
    a object with that name will be imported.

    Only uppercase variables in that object are accepted.

    :param obj: A python models, classes or a string.
    :type obj: object

    """

    def __init__(self, obj):
        self._obj = obj

    def configure(self, app):
        assert isinstance(app, Flask)
        app.config.from_object(self._obj)


class PyFileConfig(FlaskAppConfig):
    """Python File Config

    Configure app config with parameters in a python file. Only uppercase
    variables in that object are accepted.

    :param filename: Name of the config file.
    :type filename: str

    :param silent: Ignore failure of missing file when set to `True`.
    :type silent: bool

    """

    def __init__(self, filename, silent=False):
        self._filename = filename
        self._silent = silent

    def configure(self, app):
        assert isinstance(app, Flask)
        if self._filename is not None:
            app.config.from_pyfile(self._filename, silent=self._silent)


class EnvVariableConfig(FlaskAppConfig):
    """Environment Variables Config

    Configure app config from environment variables. Only variables start with
    `prefix` will be accepted.

    :param prefix: Prefix of variables that will be set into the app.
    :type prefix: str

    """

    def __init__(self, prefix=''):
        self._prefix = prefix

    def configure(self, app):
        assert isinstance(app, Flask)
        for key, val in six.iteritems(os.environ):
            if key.startswith(self._prefix):
                app.config[key] = val


class CmdVariableConfig(FlaskAppConfig):
    """Command Line Options Config

    Configure app config from command line options. Only variables start with
    `prefix` will be accepted.

    :param prefix: Prefix of variables that will be set into the app.
    :type prefix: str

    :param kwargs: Command line options.
    :type kwargs: dict

    """

    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix
        self._options = kwargs

    def configure(self, app):
        assert isinstance(app, Flask)
        for key, val in six.iteritems(self._options):
            if key.startswith(self._prefix):
                app.config[key] = val


class TileServerPreference(object):
    """Preference of Tile Server

    Preference of Tile Server includes the following options:

        - ``STONEMASON_DEBUG``:

            Set to `True` to turn on debug mode for tileserver and flask.

        - ``STONEMASON_TESTING``:

            Set to `True` to turn on testing mode for flask.

        - ``STONEMASON_GALLERY``:

            An absolute path of theme directory.

        - ``STONEMASON_CACHE``:

            A string of memcache cache servers separated by ``;`` or whitespace.

        - ``STONEMASON_VERBOSE``:

            A positive integer that represents the verbosity of log info. Set
            to 0 to turn off the logging.

        - ``STONEMASON_MAX_AGE``:

            Set ``Cache-Control`` header returned by tile api, default value is
            ``300``, which means cache control max age is 300 seconds, set
            this value to ``0`` disables ``Cache-Control``.

    """
    OPTION_PREFIX = 'STONEMASON_'

    def __init__(self, app, logger=None):
        self._app = app
        self._logger = logger

    def load(self, *configs):
        """Load a list of `FlaskAppConfig` into app

        :param configs: A list of :class:`~stonemason.service.tileserver.FlaskAppConfig`.
        :type configs: list

        """

        # load configs
        for config in configs:
            assert isinstance(config, FlaskAppConfig)
            config.configure(self._app)

        if self.debug:
            # turn on flask debug if STONEMASON_DEBUG is on
            self._app.config['DEBUG'] = True

        if self.testing:
            # turn on flask testing if STONEMASON_TESTING is on
            self._app.config['TESTING'] = True

        if self.verbose > 0 and self._logger is not None:
            # turn on logs if verbose > 0
            for key, val in six.iteritems(self._app.config):
                if key.startswith(self.OPTION_PREFIX):
                    self._logger.info('LOADED OPTION: %s=%s' % (key, val))

    @property
    def debug(self):
        """Indicate debug status of `stonemason`. Return `True` if debug is on.

        Return `True` if ``STONEMASON_DEBUG`` is set to `True`. Setting `DEBUG`
        option of `Flask` will not affect this value and only turn on flask
        debug.
        """
        return bool(self._app.config.get('STONEMASON_DEBUG', False))

    @property
    def testing(self):
        """Indicate test status of `stonemason`. Return `True` if being on
         testing

         Return `True` if ``STONEMASON_TESTING`` is set to `True`. Setting
         `TESTING` option of `Flask` will not affect this value and only turn
         on flask testing.
         """
        return bool(self._app.config.get('STONEMASON_TESTING', False))

    @property
    def theme_dir(self):
        """Return the path of theme directory

        Return the theme directory setting by ``STONEMASON_GALLERY``. Default
        is current working directory.
        """

        return self._app.config.get('STONEMASON_GALLERY', '.')

    @property
    def cache_servers(self):
        """Return a list of address of cache servers

        Return addresses of cache servers setting in ``STONEMASON_CACHE``.
        Default is `None`.

        """
        server_list = self._app.config.get('STONEMASON_CACHE', None)
        if server_list is not None:
            server_list = re.split(r'[; ]+', server_list)

        return server_list

    @property
    def verbose(self):
        """Return verbose level of logging

        Return a positive integer represents the level of logging setting
        by ``STONEMASON_VERBOSE``. Setting to `0` to turn off logging. Default
        to `0`.
        """

        try:
            verbose = int(self._app.config.get('STONEMASON_VERBOSE', 0))
        except ValueError:
            verbose = 0

        return verbose

    @property
    def max_age(self):
        """Number of seconds of max age in returned ``Cache-Control`` header,
        ``0`` means no caching. """

        try:
            max_age = int(self._app.config.get('STONEMASON_MAX_AGE', 300))
        except ValueError:
            max_age = 300

        return max_age


class TileServerApp(Flask):
    """StoneMason tile server application.

    Implements the tile map frontend service, also acting as a debugging
    all-in-one server.

    Configuration is loaded in the following order, each overwriting the
    previous ones:

        1. :class:`~stonemason.service.tileserver.default_settings`,
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

    And a health check url:

        :http:get:`/health_check`

    :type config: str
    :param config:

        Path of configuration file on your system.

    :type kwargs: dict
    :param kwargs:

        Extra configurations that could be set at start up.

    """

    def __init__(self, config=None, **kwargs):
        Flask.__init__(self, self.__class__.__name__,
                       instance_relative_config=True)

        # initialize preference
        self._preference = TileServerPreference(self)
        self._preference.load(
            # load from default settings
            ObjectConfig(default_settings),

            # load from config file
            PyFileConfig(config),

            # load from environment variables
            EnvVariableConfig(
                prefix=TileServerPreference.OPTION_PREFIX),

            # load from command line options
            CmdVariableConfig(
                prefix=TileServerPreference.OPTION_PREFIX, **kwargs)
        )

        # initialize models
        self._theme_model = ThemeModel(
            theme_dir=self._preference.theme_dir)

        theme_collection = list(self._theme_model.iter_themes())

        self._mason_model = MasonModel(
            theme_collection,
            cache_servers=self._preference.cache_servers,
            max_age=self._preference.max_age)

        # initialize blueprints
        themes_blueprint = themes.create_blueprint(
            theme_model=self._theme_model)

        maps_blueprint = maps.create_blueprint(
            mason_model=self._mason_model,
        )

        health_blueprint = health.create_blueprint()

        # register blueprints
        self.register_blueprint(themes_blueprint)
        self.register_blueprint(maps_blueprint)
        self.register_blueprint(health_blueprint)
