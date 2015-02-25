# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements theme manager.

"""

__author__ = 'ray'
__date__ = '2/20/15'

import six

from .theme import Theme


class ThemeManagerError(Exception):
    """Base Theme Error"""
    pass


class DuplicatedTheme(ThemeManagerError):
    """Duplicated Theme Error"""
    pass


class ThemeManager(object):  # pragma: no cover
    """"""

    def put(self, name, theme):
        """Put a theme into the manager

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :param theme: A `Theme` instance.
        :type name: :class:`stonemason.mason.theme.Theme`

        """
        raise NotImplementedError

    def get(self, name):
        """Get the specified theme from the manager

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :return: A `Theme` instance or None.
        :rtype: :class:`stonemason.mason.theme.Theme` or None
        """
        raise NotImplementedError

    def has(self, name):
        """Check if the specified theme is in the manager

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :return: True if the `Theme` with `name` exists.
        :rtype: bool

        """
        raise NotImplementedError

    def list(self):
        """List the names of all the themes in the manager

        :return: A list of names of all the themes.
        :rtype: list

        """
        raise NotImplementedError

    def delete(self, name):
        """Remove the specified theme from the manager

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        """
        raise NotImplementedError


class DictThemeManager(ThemeManager):
    def __init__(self):
        self._themes = dict()

    def put(self, name, theme):
        """Put a theme into the manager"""
        assert isinstance(theme, Theme)
        if self.has(name):
            raise DuplicatedTheme(name)
        self._themes[name] = theme

    def get(self, name):
        """Get the specified theme from the manager"""
        if not self.has(name):
            return None
        return self._themes[name]

    def has(self, name):
        """Check if the specified theme is in the manager"""
        return name in self._themes

    def list(self):
        """List the names of all the themes in the manager"""
        return list(name for name in six.iterkeys(self._themes))

    def delete(self, name):
        """Remove the specified theme from the manager"""
        if self.has(name):
            del self._themes[name]

