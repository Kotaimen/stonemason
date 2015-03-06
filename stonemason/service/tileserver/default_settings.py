# -*- encoding: utf-8 -*-
"""
    stonemason.service.tileserver.default_settings
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Default configuration for the tile server

"""

# Set to `True` to turn on debug mode for tileserver and flask.
STONEMASON_DEBUG = False


# Set to `True` to turn on testing mode for flask.
STONEMASON_TESTING = False

# An absolute path of theme directory.
STONEMASON_THEMES = '.'

# A string of memcache cache servers seperated by ``;`` or blank.
STONEMASON_CACHE = None

# Set a positive integer that represents the verbosity of the logging. Set
# to 0 to turn off the logging.
STONEMASON_VERBOSE = 0

# Cache control max age of tile api
STONEMASON_MAX_AGE = 300
