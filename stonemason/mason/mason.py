# -*- encoding: utf-8 -*-
"""
    stonemason.mason.mason
    ~~~~~~~~~~~~~~~~~~~~~~
    Facade of StoneMason.

"""

from collections import namedtuple

from .builder import TileProviderFactory
from .theme import Theme, ThemeManager


class MasonError(Exception):
    """Base Mason Error"""
    pass


class ThemeNotExist(MasonError):
    """`Theme` is not found"""
    pass


class ThemeAlreadyLoaded(MasonError):
    """`Theme` has already been loaded"""
    pass


class ThemeNotLoaded(MasonError):
    """`Theme` has not been loaded"""
    pass


class Mason(object):
    """Stonemason Facade

    `Mason` is the facade of `Stonemason`. A `Mason` object provides tiles of
    various kinds of themes from caches, storage and renders.

    Themes could be loaded or unloaded by their names. Though, these with
    duplicated names are not allowed.

    In `Mason`, tiles are served according to their tags which, for now,
    equals to the name of their themes.

    :param theme_store: A `ThemeManager` instance that contains piles of themes.
    :type theme_store: :class:`stonemason.mason.theme.ThemeManager`

    :param readonly: A bool variable that controls serving mode of `Mason`.
    :type readonly: bool

    """

    def __init__(self,
                 readonly=False,
                 logger=None,
                 default_cache_config=None):
        assert isinstance(readonly, bool)
        assert isinstance(default_cache_config, dict) or \
               default_cache_config is None

        self._logger = logger
        self._readonly = readonly
        self._default_cache_config = default_cache_config

        self._builder = TileProviderFactory()
        self._providers = dict()

    def load_theme(self, theme):
        """Load the named theme"""
        tag = theme.name

        if tag in self._providers:
            raise ThemeAlreadyLoaded(tag)

        provider = self._builder.create_from_theme(
            tag, theme, cache_config=self._default_cache_config)

        if self._readonly:
            provider.readonly = True

        self._providers[tag] = provider

    def get_tile(self, tag, z, x, y, scale, ext):
        """Get a tile with the given tag and parameters"""

        try:
            provider = self._providers[tag]
        except KeyError:
            return None
        else:
            tile = provider.get_tile(z, x, y)
            return tile

    def get_tile_tags(self):
        """Get all available tile tags"""
        return list(tag for tag in self._providers)

