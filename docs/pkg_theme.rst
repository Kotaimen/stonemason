Theme Definition
================

:mod:`stonemason.mason.theme.Theme`

A theme is the main configuration for stonemason. Stonemason creates various
kinds of providers from different themes.

A theme is composed of the following blocks:

- `MetadataBlock`, which contains various settings for running a provider.
- `ModeBlock`, which controls how a provider should run.
- `CacheBlock`, which contains options for cache used by a provider.
- `StorageBlock`, which contains options for storage used by a provider.
- `DesignBlock`, the definition of styles for tile rendering.


Exceptions
~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.ThemeBlockError
    :members:

.. autoclass:: stonemason.mason.theme.MetadataValueError
    :members:


MetadataBlock
~~~~~~~~~~~~~

.. autoclass:: stonemason.mason.theme.MetadataBlock
    :members:
