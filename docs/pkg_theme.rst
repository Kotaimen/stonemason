Theme System
************

.. module:: stonemason.mason.theme

The `Theme` module is the configuration module for stonemason. By setting up
configurations in a theme file, you tell stonemason how and where to load all
the map books and also critical information to assemble various components of
these map books.


Exceptions
==========

.. autoclass:: stonemason.mason.theme.ThemeError

.. autoclass:: stonemason.mason.theme.ThemeConfigNotFound

.. autoclass:: stonemason.mason.theme.InvalidThemeConfig


Theme
=====

.. autoclass:: stonemason.mason.theme.Theme
    :members:


Curator
=======

.. autoclass:: stonemason.mason.theme.Curator
    :members:

.. autoclass:: stonemason.mason.theme.FileSystemCurator
    :members:


Gallery
=======

.. autoclass:: stonemason.mason.theme.Gallery
    :members:

.. autoclass:: stonemason.mason.theme.MemGallery
    :members:
