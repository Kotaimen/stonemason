# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.loader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme loader for theme manager.

"""

__author__ = 'ray'
__date__ = '2/8/15'

import os
import six
import json

from .theme import Theme
from .manager import ThemeManager


def is_valid_theme_filename(filename):
    """Check if is a theme file"""
    # TODO: USE YAML FORMAT INSTEAD
    _, ext = os.path.splitext(filename)
    return ext == '.json'


def patch_file_path(root, configs):
    if 'design' in configs:
        if 'layers' in configs['design']:
            layers = configs['design']['layers']
            assert isinstance(layers, dict)
            for name, layer in six.iteritems(layers):
                for k, v in six.iteritems(layer):
                    if k == 'style_sheet':
                        if not os.path.isabs(v):
                            v = os.path.join(root, v)
                            configs['design']['layers'][name][k] = v

    return configs


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

    def __init__(self, theme_root, theme_name):
        self._theme_root = theme_root
        self._theme_file = os.path.join(self._theme_root, theme_name)

    def load_into(self, manager):
        """Load themes into the manager"""
        assert isinstance(manager, ThemeManager)

        with open(self._theme_file, 'r') as fp:
            configs = json.loads(fp.read())

            # TODO: Fix this temporary patch
            configs = patch_file_path(self._theme_root, configs)

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

    def __init__(self, theme_dir):
        self._theme_dir = theme_dir

    def load_into(self, manager):
        """Load themes into the manager"""
        assert isinstance(manager, ThemeManager)

        loaded = list()

        for theme_name in os.listdir(self._theme_dir):
            if not is_valid_theme_filename(theme_name):
                continue
            loader = JsonThemeLoader(self._theme_dir, theme_name)
            loaded.extend(loader.load_into(manager))

        return loaded
