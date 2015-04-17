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
from .exceptions import InvalidThemeConfig, ThemeConfigNotFound


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
    MANIFEST_FILE = 'manifest.mason'

    def __init__(self, theme_root):
        self._theme_root = theme_root

    def add_to(self, gallery):
        assert isinstance(gallery, Gallery)

        for filename in self.walk():
            if not is_valid_theme_filename(filename):
                continue

            basename, filename = os.path.split(filename)

            template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(basename))

            env_l = {}
            env_g = {}

            template = template_env.get_template(filename)
            template_variables = dict(theme_root=basename)

            source = template.render(**template_variables).encode('utf-8')
            # print (source)
            exec (source, env_g, env_l)

            theme_config = env_l.get('THEME')
            self.validate(theme_config)

            theme = Theme(**theme_config)

            gallery.put(theme.name, theme)

    def walk(self):
        manifest = os.path.join(self._theme_root, self.MANIFEST_FILE)

        if os.path.exists(manifest):
            with open(manifest, 'r') as fp:
                for path in fp.readlines():
                    filename = os.path.join(self._theme_root, path.strip())
                    if not os.path.exists(filename):
                        raise ThemeConfigNotFound(filename)
                    yield filename
        else:
            for name in os.listdir(self._theme_root):
                filename = os.path.join(self._theme_root, name)
                yield filename

    def validate(self, theme_config):
        if not isinstance(theme_config, dict):
            raise InvalidThemeConfig('"THEME" should be a dict object')


