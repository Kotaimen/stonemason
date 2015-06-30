# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements configuration system for stonemason.

"""

import os

from .theme import Theme, SchemaTheme
from .gallery import Gallery, MemGallery
from .curator import Curator, FileSystemCurator

from .exceptions import ThemeError, ThemeConfigNotFound, InvalidThemeConfig


SAMPLE_THEME_DIRECTORY = os.path.join(os.path.dirname(__file__), 'samples')

SAMPLE_THEME_NAME = 'sample_world.mason'

SAMPLE_THEME = os.path.join(SAMPLE_THEME_DIRECTORY, SAMPLE_THEME_NAME)
