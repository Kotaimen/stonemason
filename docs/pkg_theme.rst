Theme
=====

:mod:`stonemason.mason.theme`

A `Theme` is the main configuration for stonemason. Stonemason creates
various kinds of providers from different themes.

Normally, a theme contains the following configs:

**Setup Configs**:

- :class:`~stonemason.mason.theme.PyramidConfig`

    Tile Grid of a `Provider`.

- :class:`~stonemason.mason.theme.MetadataConfig`

    Basic information about a `Provider`.

- :class:`~stonemason.mason.theme.CacheConfig`

    Options for creating a :class:`~stonemason.provider.tilecache.TileCache`.

- :class:`~stonemason.mason.theme.StorageConfig`

    Options for creating a :class:`~stonemason.provider.tilestorage.TileStorage`.

**Rendering Configs**:

- `DesignConfig`

    definitions of styles for layers in tile rendering.


Exceptions
~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.ThemeError
    :members:


Configs
~~~~~~~

.. autoclass:: stonemason.mason.theme.PyramidConfig
    :members:


.. autoclass:: stonemason.mason.theme.PyramidConfig
    :members:

.. autoclass:: stonemason.mason.theme.CacheConfig
    :members:

.. autoclass:: stonemason.mason.theme.StorageConfig
    :members:


Theme
~~~~~


.. autoclass:: stonemason.mason.theme.Theme
    :members:
