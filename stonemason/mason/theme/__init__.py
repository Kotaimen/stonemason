# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements details of theme for stonemason

"""

import os

from .parser import JsonThemeParser
from .theme import MetadataConfig, PyramidConfig, CacheConfig, StorageConfig, \
    Theme, ThemeError

SAMPLE_THEME_DIRECTORY = os.path.join(
    os.path.dirname(__file__), 'samples')

SAMPLE_THEME = os.path.join(
    SAMPLE_THEME_DIRECTORY, 'sample_theme.json')
