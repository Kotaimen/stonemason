# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme loader for theme manager.

"""

__author__ = 'ray'
__date__ = '2/8/15'

import os
import json

from .theme import Theme
from .manager import ThemeManager


def is_valid_theme_filename(filename):
    """Check if is a theme file"""
    # TODO: USE YAML FORMAT INSTEAD
    _, ext = os.path.splitext(filename)
    return ext == '.json'


class ThemeLoader(object):  # pragma: no cover
    """Base Theme Loader

    A `ThemeLoader` could parse and load themes into a theme manager.
    """

    def load_into(self, manager):
        """Subclass should implement this method

        :param manager: A :class:`~stonemason.mason.theme.ThemeManager` object.
        :type manager: :class:`~stonemason.mason.theme.ThemeManager`

        :return: A list of the names of loaded themes.
        :rtype: list
        """
        raise NotImplementedError


class JsonThemeLoader(ThemeLoader):
    """Json Theme Loader

    A `FileThemeLoader` could parses and loads a json theme into a theme
    manager.

    :param filename: A string literal represents the full path of a file.
    :type filename: str

    """

    def __init__(self, filename):
        self._filename = filename

    def load_into(self, manager):
        """Load themes into the manager"""
        assert isinstance(manager, ThemeManager)

        with open(self._filename, 'r') as fp:
            configs = json.loads(fp.read())

            theme = Theme(**configs)
            manager.put(theme.name, theme)

            return [theme.name]


class YAMLThemeLoader(ThemeLoader):
    # TODO: Implement yaml theme format
    pass


class LocalThemeLoader(ThemeLoader):
    """Local Theme Directory Loader

    A `LocalThemeLoader` could parse and load themes in a given directory.

    :param dirname: A string literal represents the full path of a directory.
    :type dirname: str

    """

    def __init__(self, dirname):
        self._dirname = dirname

    def load_into(self, manager):
        """Load themes into the manager"""
        assert isinstance(manager, ThemeManager)

        loaded = list()

        for basename in os.listdir(self._dirname):

            filename = os.path.join(self._dirname, basename)
            if not is_valid_theme_filename(filename):
                continue

            file_loader = JsonThemeLoader(filename)
            loaded.extend(file_loader.load_into(manager))

        return loaded
