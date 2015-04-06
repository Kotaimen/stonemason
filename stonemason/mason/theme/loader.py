# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme loader for theme manager.

"""

__author__ = 'ray'
__date__ = '2/8/15'

import os

import jinja2

from .theme import MapTheme
from .manager import ThemeManager
from .exceptions import ThemeLoaderError


def is_valid_theme_file(filename):
    """Check if is a theme file"""
    _, ext = os.path.splitext(filename)
    return ext == '.mason'


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


class FileSystemThemeLoader(ThemeLoader):
    def __init__(self, theme_root):
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(theme_root))
        self._theme_root = theme_root

    def load_into(self, manager):
        assert isinstance(manager, ThemeManager)

        for theme_name in os.listdir(self._theme_root):
            if not is_valid_theme_file(theme_name):
                continue

            env_l = {}
            env_g = {}

            template = self._env.get_template(theme_name)
            template_variables = dict(theme_root=self._theme_root)
            source = template.render(**template_variables).encode('utf-8')
            # print (source)
            exec (source, env_g, env_l)

            try:
                theme_config = env_l['THEME']
                if not isinstance(theme_config, dict):
                    raise ThemeLoaderError('"THEME" should be a dict object')
            except KeyError:
                raise ThemeLoaderError('Missing Theme object"THEME"')

            map_theme = MapTheme(**theme_config)
            manager.put(map_theme.name, map_theme)




