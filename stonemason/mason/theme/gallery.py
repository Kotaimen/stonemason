# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.gallery
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the interface of theme container and its different implementations.

"""

__author__ = 'ray'
__date__ = '2/20/15'

import collections

from .theme import Theme


class Gallery(object):  # pragma: no cover
    """Theme Gallery Interface

    In stonemason, a `Gallery` serves as a container and manager for storing,
    querying and indexing themes.

    Detailed implementation should be taken care of by subclasses of the
    `Gallery`. Backend storage could be memory, disk or remote service.

    """

    def put(self, name, theme):
        """Put a theme into the gallery.

        :param name: A string literal uniquely identifies the theme.
        :type name: str

        :param theme: A `Theme` instance.
        :type name: :class:`~stonemason.mason.theme.Theme`

        """
        raise NotImplementedError

    def get(self, name):
        """Get a theme from the gallery with the given name.

        :param name: A string literal uniquely identifies the theme.
        :type name: str

        :return: A `Theme` instance or None.
        :rtype: :class:`~stonemason.mason.theme.Theme` or None
        """
        raise NotImplementedError

    def has(self, name):
        """Check if the theme with the given name is in the gallery.

        :param name: A string literal uniquely identifies the theme.
        :type name: str

        :return: True if exists.
        :rtype: bool

        """
        raise NotImplementedError

    def delete(self, name):
        """Remove the specified theme from the gallery.

        :param name: A string literal uniquely identifies the theme.
        :type name: str

        """
        raise NotImplementedError

    def __iter__(self):
        """Return an iterator of theme names in the gallery.

        :return: Return an iterator of theme names.
        :rtype: generator

        """
        raise NotImplementedError


class MemGallery(Gallery):
    """Memory Gallery

    `MemGallery` is a in-memory implementation of `Gallery` which manages themes
    in the local memory. It is simple and fast but it is not
    thread-safe and conflict free.

    """

    def __init__(self):
        self._themes = collections.OrderedDict()

    def put(self, name, theme):
        assert isinstance(theme, Theme)
        self._themes[name] = theme

    def get(self, name):
        try:
            return self._themes[name]
        except KeyError:
            return None

    def delete(self, name):
        try:
            del self._themes[name]
        except KeyError:
            pass  # do not complain if theme not exists

    def has(self, name):
        return name in self._themes

    def __iter__(self):
        return iter(self._themes)

