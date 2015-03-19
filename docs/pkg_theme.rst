Theme System
************

.. module:: stonemason.mason.theme

A `Theme` is the main configuration for stonemason. It defines a large amount
of configs for a :class:`~stonemason.provider.tileprovider.TileProvider` to
serve tiles from different kinds of storage.

.. autoclass:: stonemason.mason.theme.Theme
    :members:

Exceptions
==========

.. autoclass:: stonemason.mason.theme.ThemeError
    :members:

Elements
========

.. autoclass:: stonemason.mason.theme.ThemeElement
    :members:

.. autoclass:: stonemason.mason.theme.ThemeMetadata
    :members:

.. autoclass:: stonemason.mason.theme.ThemePyramid
    :members:

.. autoclass:: stonemason.mason.theme.ThemeCache
    :members:

.. autoclass:: stonemason.mason.theme.ThemeStorage
    :members:


Loaders
=======

.. autoclass:: stonemason.mason.theme.ThemeLoader
    :members:

.. autoclass:: stonemason.mason.theme.JsonThemeLoader

.. autoclass:: stonemason.mason.theme.LocalThemeLoader


Managers
========

.. autoclass:: stonemason.mason.theme.ThemeManager
    :members:

.. autoclass:: stonemason.mason.theme.MemThemeManager


