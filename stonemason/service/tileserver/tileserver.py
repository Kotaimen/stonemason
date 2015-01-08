# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver.tileserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the tile server for Stonemason.

"""
import os
from flask import Flask

from . import default_settings


class AppBuilder(object):
    """ Application Builder
    """

    def build(self, config=None):
        app = Flask(__name__, instance_relative_config=True)

        # config from default settings
        app.config.from_object(default_settings)

        # config from setting file
        if config is not None:
            app.config.from_pyfile(config, silent=True)

        # config from system environment parameters
        for key, val in os.environ.items():
            if key.startswith('EXAMPLE_APP_'):
                app.config[key] = val

        if app.config['EXAMPLE_APP_MODE'] == 'development':
            app.config['DEBUG'] = True
            app.config['TESTING'] = True

        @app.route('/')
        def hello_world():
            return 'Hello World!'

        return app
