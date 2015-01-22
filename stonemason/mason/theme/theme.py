# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.theme
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Defines the format of stonemason theme.

"""

from collections import namedtuple

_ThemeElement = namedtuple('_Foo', 'prototype parameters')


class ThemeError(Exception):
    """Base Theme Error"""
    pass


class Validator(object):
    """Validator Interface

    A validator subclass should implement the detail of the validation.
    """

    def validate(self):
        """Return true if is valid"""
        raise NotImplementedError


class ThemeElement(_ThemeElement, Validator):
    """Theme Element

    Each element in a theme has a property called `prototype`, which is
    used to specify the type of the element a provider will use. And a
    `parameters` property determines how to create this element.

    `prototype`

        Type of the element a provider will use.

    `parameters`

        Parameters of the element.

    """

    def validate(self):
        raise NotImplementedError


class ThemeCache(ThemeElement):
    def validate(self):
        return False


class ThemeStorage(ThemeElement):
    def validate(self):
        return False


class ThemeDesign(ThemeElement):
    def validate(self):
        return False


class Theme(object):
    """ Map Theme

    The theme object is a specialized config for providers.
    It defines cache, storage, design and a bunch of options of
    a map provider.

    `config`

        :class:`stonemason.mason.config.Config`

    """

    def __init__(self, config):
        self._name = config.get('name')

        conf = config.get('cache')
        if conf is not None:
            self._cache = ThemeCache(conf['prototype'], conf['parameters'])
            self._cache.validate()

        conf = config.get('storage')
        if conf is not None:
            self._storage = ThemeStorage(conf['prototype'], conf['parameters'])
            self._storage.validate()

        conf = config.get('design')
        if conf is not None:
            self._design = ThemeDesign(conf['prototype'], conf['parameters'])
            self._design.validate()

        self._metadata = config.get('metadata', dict())
        if not isinstance(self._metadata, dict):
            self._metadata = dict()

    @property
    def name(self):
        """Name of the theme"""
        return self._name

    @property
    def metadata(self):
        """Metadata of the theme"""
        return self._metadata

    @property
    def cache(self):
        """Cache configuration"""
        return self._cache

    @property
    def storage(self):
        """Storage configuration"""
        return self._storage

    @property
    def design(self):
        """Map design for renderer"""
        return self._design
