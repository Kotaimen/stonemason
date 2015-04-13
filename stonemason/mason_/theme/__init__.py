# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements `Theme` and `ThemeManager` for stonemason

"""

import os

from .theme import Theme, TileMatrixTheme
from .gallery import Gallery, MemGallery
from .curator import Curator, FileSystemCurator

from .exceptions import ThemeError


SAMPLE_THEME_DIRECTORY = os.path.join(os.path.dirname(__file__), 'samples')

SAMPLE_THEME_NAME = 'sample_world.mason'

SAMPLE_THEME = os.path.join(SAMPLE_THEME_DIRECTORY, SAMPLE_THEME_NAME)
