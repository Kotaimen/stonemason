Theme System
============

.. module:: stonemason.mason.theme

A `Theme` is the main configuration for stonemason. It defines a large amount
of configs for a :class:`~stonemason.provider.tileprovider.TileProvider` to
serve tiles from different kinds of storage.


Exceptions
~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.ThemeError
    :members:


Theme
~~~~~

.. autoclass:: stonemason.mason.theme.Theme
    :members:



Theme Config
~~~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.MetadataConfig
    :members:

.. autoclass:: stonemason.mason.theme.PyramidConfig
    :members:

.. autoclass:: stonemason.mason.theme.CacheConfig
    :members:

.. autoclass:: stonemason.mason.theme.StorageConfig
    :members:


Theme Parser
~~~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.JsonThemeParser
    :members:

