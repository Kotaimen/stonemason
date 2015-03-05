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
    """Theme Manager Interface

    In stonemason, `ThemeManager` serves as a container and manager for storing
    querying and indexing themes.

    It could be implemented with a local memory dict, a disk storage, or even
    a remote service.

    Subclasses should take care of the detail implementation.

    """

    def put(self, name, theme):
        """Put a theme into the manager and returns nothing.

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :param theme: A `Theme` instance.
        :type name: :class:`~stonemason.mason.theme.Theme`

        """
        raise NotImplementedError

    def get(self, name):
        """Get the specified theme from the manager.

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :return: A `Theme` instance or None.
        :rtype: :class:`~stonemason.mason.theme.Theme` or None
        """
        raise NotImplementedError

    def has(self, name):
        """Check if the specified theme exists.

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        :return: True if the `Theme` with `name` exists.
        :rtype: bool

        """
        raise NotImplementedError

    def delete(self, name):
        """Remove the specified theme from the manager and returns nothing.

        :param name: A string literal represents uniquely identify the theme.
        :type name: str

        """
        raise NotImplementedError

    def iternames(self):
        """Iterate theme names in the manager.

        :return: Return a generator of names in the manager.
        :rtype: generator

        """
        raise NotImplementedError

    def iterthemes(self):
        """Iterate themes in the manager.

        :return: Return a generator of themes in the manager.
        :rtype: generator

        """
        raise NotImplementedError

    def __iter__(self):
        """Iterate name and theme in the manager.

        :return: Return a generator of (name, theme) in the manager.
        :rtype: generator

        """
        raise NotImplementedError


class MemThemeManager(ThemeManager):
    """Memory Theme Manager

    `MemThemeManager` is a in-memory implementation of `ThemeManager`. It
    manages and operates themes in the local memory.

    """

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

    def delete(self, name):
        """Remove the specified theme from the manager"""
        if self.has(name):
            del self._themes[name]

    def iternames(self):
        """Iterate theme names in the manager"""
        return six.iterkeys(self._themes)

    def iterthemes(self):
        """Iterate themes in the manager"""
        return six.itervalues(self._themes)

    def __iter__(self):
        """Iterate name and theme in the manager"""
        return six.iteritems(self._themes)

