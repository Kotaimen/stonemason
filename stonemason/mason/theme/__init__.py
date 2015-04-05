# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements `Theme` and `ThemeManager` for stonemason

"""

import os

from .theme import MapTheme
from .manager import ThemeManager, MemThemeManager
from .loader import ThemeLoader, PythonThemeLoader, LocalThemeLoader

from .exceptions import ThemeError, ThemeManagerError


SAMPLE_THEME_DIRECTORY = os.path.join(
    os.path.dirname(__file__), 'samples', 'sample_world')

SAMPLE_THEME_NAME = 'sample_world.mason'

SAMPLE_THEME = os.path.join(SAMPLE_THEME_DIRECTORY, SAMPLE_THEME_NAME)
