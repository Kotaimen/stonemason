Theme
=====

:mod:`stonemason.mason.theme`

A `Theme` is the main configuration for stonemason. Stonemason creates
various kinds of providers from different themes.

It is composed of the following blocks:

**Setup Blocks**:

- :class:`~stonemason.mason.theme.MetadataBlock`

    Various options for setting up a `Provider`.

- :class:`~stonemason.mason.theme.CacheBlock`

    Options for creating a :class:`~stonemason.provider.tilecache.TileCache`.

- :class:`~stonemason.mason.theme.StorageBlock`

    Options for creating a :class:`~stonemason.provider.tilestorage.TileStorage`.

**Control Blocks**:

- :class:`~stonemason.mason.theme.ModeBlock`

    Running behaviours of a `Provider`.

**Rendering Blocks**:

- :class:`~stonemason.mason.theme.DesignBlock`

    definitions of styles for layers in tile rendering.


Exceptions
~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.FieldTypeError
    :members:

.. autoclass:: stonemason.mason.theme.ValidationError
    :members:


Theme Blocks
~~~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.MetadataBlock
    :members:

.. autoclass:: stonemason.mason.theme.CacheBlock
    :members:

.. autoclass:: stonemason.mason.theme.StorageBlock
    :members:

.. autoclass:: stonemason.mason.theme.ModeBlock
    :members:


