# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.curator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements loaders for gallery.

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

    A `Curator` parses and loads themes into a theme
    :class:`~stonemason.mason.theme.Gallery`.
    """

    def add_to(self, gallery):
        """Subclass should implement this method

        :param gallery: An instance of :class:`~stonemason.mason.theme.Gallery`.
        :type gallery: :class:`~stonemason.mason.theme.Gallery`

        """
        raise NotImplementedError


class FileSystemCurator(Curator):
    """File System Curator

    A `FileSystemCurator` parses and loads themes from local file system.

    A manifest file `manifest.mason` will be looked up first to get a list of
    locations of available themes to load. If the manifest file does not exists,
    the theme files in the current directory will be loaded. A valid theme file
    name should ends with the extension ``mason``. Each line in the manifest
    represents one location of the theme file.

    Example:

    .. code-block:: shell

        ./samples/sample_world/sample_world.mason
        ./samples/sample_world/sample_proj.mason
        ./samples/sample_world/sample_proj.mason

    You could comment out a theme with a `#` at the start of the line:

    .. code-block:: shell

        #./samples/sample_world/sample_proj.mason


    """
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

            data_root = os.path.join(os.environ['HOME'], 'proj/geodata/')
            template_variables = dict(theme_root=basename, data_root=data_root)

            source = template.render(**template_variables).encode('utf-8')
            # print (source)
            exec (source, env_g, env_l)

            theme_config = env_l.get('THEME')
            self.validate(theme_config)

            theme = Theme(**theme_config)

            gallery.put(theme.name, theme)

    def walk(self):
        """Find the manifest file and iterate filename of the themes."""
        manifest = os.path.join(self._theme_root, self.MANIFEST_FILE)

        if os.path.exists(manifest):
            with open(manifest, 'r') as fp:
                for line in fp.readlines():
                    path = line.strip()
                    if not path or path.startswith('#'):
                        continue
                    filename = os.path.join(self._theme_root, path.strip())
                    if not os.path.exists(filename):
                        raise ThemeConfigNotFound(filename)
                    yield filename
        else:
            for name in os.listdir(self._theme_root):
                filename = os.path.join(self._theme_root, name)
                yield filename

    def validate(self, theme_config):
        """Valid the format of a theme config"""
        if not isinstance(theme_config, dict):
            raise InvalidThemeConfig('"THEME" should be a dict object')
