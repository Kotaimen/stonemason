# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements `Theme` and `ThemeManager` for stonemason

"""

import os

from .theme import ThemeError, InvalidThemeValue
from .theme import Theme, ThemeElement
from .theme import ThemeMetadata, ThemePyramid, ThemeCache, ThemeStorage

from .manager import ThemeManagerError, DuplicatedTheme
from .manager import ThemeManager, MemThemeManager
from .loader import ThemeLoader, JsonThemeLoader, LocalThemeLoader


SAMPLE_THEME_DIRECTORY = os.path.join(os.path.dirname(__file__), 'samples')

SAMPLE_THEME = os.path.join(SAMPLE_THEME_DIRECTORY, 'sample_theme.json')
