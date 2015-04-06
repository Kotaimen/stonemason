Theme System
************

.. module:: stonemason.mason.theme

A `Theme` is the main configuration for stonemason. It defines a large amount
of configs for a :class:`~stonemason.provider.tileprovider.TileProvider` to
serve tiles from different kinds of storage.


Loaders
=======

.. autoclass:: stonemason.mason.theme.ThemeLoader
    :members:

.. autoclass:: stonemason.mason.theme.FileSystemThemeLoader


Managers
========

.. autoclass:: stonemason.mason.theme.ThemeManager
    :members:

.. autoclass:: stonemason.mason.theme.MemThemeManager


