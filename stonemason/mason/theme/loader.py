# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme loader for theme manager.

"""

__author__ = 'ray'
__date__ = '2/8/15'

import os

from .theme import MapTheme
from .manager import ThemeManager
from .exceptions import ThemeLoaderError


def is_map_theme(filename):
    """Check if is a theme file"""
    _, ext = os.path.splitext(filename)
    return ext == '.mason'


def make_abspath_func(root):
    def func(path):
        if not os.path.isabs(path):
            path = os.path.join(root, path)
        return path

    return func


class ThemeLoader(object):  # pragma: no cover
    """Base Theme Loader

    A `ThemeLoader` could parse and load themes into a theme manager.
    """

    def load_into(self, manager):
        """Subclass should implement this method

        :param manager: A :class:`~stonemason.mason.theme.ThemeManager` object.
        :type manager: :class:`~stonemason.mason.theme.ThemeManager`

        """
        raise NotImplementedError


class PythonThemeLoader(ThemeLoader):
    def __init__(self, filename):
        self._filename = filename
        self._theme_root = os.path.dirname(filename)

    def load_into(self, manager):
        assert isinstance(manager, ThemeManager)

        env_g = {}
        env_l = {'URI': make_abspath_func(self._theme_root)}
        with open(self._filename, 'r') as fp:
            code = compile(fp.read(), self._filename, 'exec')
            exec (code, env_g, env_l)

        try:
            theme_config = env_l['THEME']
            if not isinstance(theme_config, dict):
                raise ThemeLoaderError('"THEME" should be a dict object')
        except KeyError:
            raise ThemeLoaderError('Missing Theme object"THEME"')

        map_theme = MapTheme(**theme_config)
        manager.put(map_theme.name, map_theme)


class LocalThemeLoader(ThemeLoader):
    """Local Theme Directory Loader

    A `LocalThemeLoader` could parse and load themes in a given directory.

    :param collection_root: Full path of a theme directory.
    :type collection_root: str

    """

    def __init__(self, collection_root):
        self._collection_root = collection_root

    def load_into(self, manager):
        assert isinstance(manager, ThemeManager)

        for basename in os.listdir(self._collection_root):
            if not is_map_theme(basename):
                continue

            filename = os.path.join(self._collection_root, basename)

            loader = PythonThemeLoader(filename)
            loader.load_into(manager)



