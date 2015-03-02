# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A high performance tile server WSGI application based on Flask.
"""

import os

import six
from flask import Flask

from .models import ThemeModel, MasonModel
from . import themes
from . import tiles
from . import maps
from . import health
from . import admin
from . import default_settings


class FlaskAppConfig(object):
    def configure(self, app):
        raise NotImplementedError


class DefaultConfig(FlaskAppConfig):
    def __init__(self, obj):
        self._obj = obj

    def configure(self, app):
        assert isinstance(app, Flask)
        app.config.from_object(self._obj)


class PyFileConfig(FlaskAppConfig):
    def __init__(self, filename, silent=False):
        self._filename = filename
        self._silent = silent

    def configure(self, app):
        assert isinstance(app, Flask)
        if self._filename is not None:
            app.config.from_pyfile(self._filename, silent=self._silent)


class EnvVariableConfig(FlaskAppConfig):
    def __init__(self, prefix=''):
        self._prefix = prefix

    def configure(self, app):
        assert isinstance(app, Flask)
        for key, val in six.iteritems(os.environ):
            if key.startswith(self._prefix):
                app.config[key] = val


class CmdVariableConfig(FlaskAppConfig):
    def __init__(self, prefix='', **kwargs):
        self._prefix = prefix
        self._options = kwargs

    def configure(self, app):
        assert isinstance(app, Flask)
        for key, val in six.iteritems(self._options):
            if key.startswith(self._prefix):
                app.config[key] = val


class TileServerPreference(object):
    OPTION_PREFIX = 'STONEMASON_'

    def __init__(self, app, logger=None):
        self._app = app
        self._logger = logger

    def load(self, *configs):
        for config in configs:
            assert isinstance(config, FlaskAppConfig)
            config.configure(self._app)

        if self.debug:
            self._app.config['DEBUG'] = True

        if self.testing:
            self._app.config['TESTING'] = True

        if self.verbose > 0 and self._logger is not None:
            for key, val in six.iteritems(self._app.config):
                if key.startswith(self.OPTION_PREFIX):
                    self._logger.info('LOADED OPTION: %s=%s' % (key, val))

    @property
    def debug(self):
        return bool(self._app.config.get('STONEMASON_DEBUG', False))

    @property
    def testing(self):
        return bool(self._app.config.get('STONEMASON_TESTING', False))

    @property
    def theme_dir(self):
        return self._app.config.get('STONEMASON_THEMES', '.')

    @property
    def cache_servers(self):
        return self._app.config.get('STONEMASON_MEMCACHE_HOSTS', None)

    @property
    def verbose(self):
        try:
            verbose = int(self._app.config.get('STONEMASON_VERBOSE', 0))
        except ValueError:
            verbose = 0
        return verbose


class TileServerApp(Flask):
    def __init__(self, config=None, **kwargs):
        Flask.__init__(self, self.__class__.__name__,
                       instance_relative_config=True)

        # initialize preference
        self._preference = TileServerPreference(self)
        self._preference.load(
            # load from default settings
            DefaultConfig(default_settings),

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

        self._mason_model = MasonModel(
            self._theme_model, cache_servers=self._preference.cache_servers)

        themes_blueprint = themes.create_blueprint(
            theme_model=self._theme_model)
        self.register_blueprint(themes_blueprint)

        tiles_blueprint = tiles.create_blueprint(
            mason_model=self._mason_model
        )
        self.register_blueprint(tiles_blueprint)

        maps_blueprint = maps.create_blueprint(
            mason_model=self._mason_model, theme_model=self._theme_model
        )
        self.register_blueprint(maps_blueprint)

        health_blueprint = health.create_blueprint()
        self.register_blueprint(health_blueprint)

        admin_blueprint = admin.create_blueprint(
            mason_model=self._mason_model, theme_model=self._theme_model
        )
        self.register_blueprint(admin_blueprint)
