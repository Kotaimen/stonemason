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

from .theme import Theme
from .gallery import Gallery
from .exceptions import ThemeError, InvalidThemeConfig


def is_valid_theme_filename(filename):
    """Check if is a theme file"""
    _, ext = os.path.splitext(filename)
    return ext == '.mason'


class Curator(object):  # pragma: no cover
    """Base Theme Loader

    A `ThemeLoader` could parse and load themes into a theme manager.
    """

    def add_to(self, gallery):
        """Subclass should implement this method

        :param gallery: A :class:`~stonemason.mason.theme.Gallery` object.
        :type gallery: :class:`~stonemason.mason.theme.Gallery`

        """
        raise NotImplementedError


class FileSystemCurator(Curator):
    def __init__(self, theme_root, silent=True):
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(theme_root))
        self._theme_root = theme_root
        self._silent = silent

    def add_to(self, gallery):
        assert isinstance(gallery, Gallery)

        for theme_name in os.listdir(self._theme_root):
            if not is_valid_theme_filename(theme_name):
                continue

            env_l = {}
            env_g = {}

            template = self._env.get_template(theme_name)
            template_variables = dict(theme_root=self._theme_root)
            source = template.render(**template_variables).encode('utf-8')
            # print (source)
            exec (source, env_g, env_l)

            theme_config = env_l.get('THEME')
            if not self.validate(theme_config):
                continue

            map_theme = Theme(**theme_config)

            gallery.put(map_theme.name, map_theme)

    def validate(self, theme_config):
        try:
            if not isinstance(theme_config, dict):
                raise InvalidThemeConfig('"THEME" should be a dict object')
        except ThemeError as e:
            if self._silent:
                return False
            raise e
        return True


