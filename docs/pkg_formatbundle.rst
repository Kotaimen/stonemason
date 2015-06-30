Map Format
**********

.. module::stonemason.formatbundle

:mod:`stonemason.formatbundle` defines map types, tile formats and
their conversions.

.. warning:: Contents of this package are subject to change if dynamic
    format registering is implemented.


Exceptions
==========

.. automodule:: stonemason.formatbundle.exceptions
    :members:
    :undoc-members:


Map Type
========

.. autoclass:: stonemason.formatbundle.MapType
    :members:

Tile Format
===========

.. autoclass:: stonemason.formatbundle.TileFormat
    :members:

Common Image Formats
--------------------

See `pillow file formats <https://pillow.readthedocs.org/handbook/image-file-formats.html>`_
for a complete list of image format parameters.

    =======  ============= ========= =======================================
    Format   Mimetype      Extension Common Parameters
    =======  ============= ========= =======================================
    JPEG     image/jpeg    .jpg      ``quality``, ``optimized``
    PNG      image/png     .png      ``quality``
    =======  ============= ========= =======================================


.. note:: `Pillow` don't convert colorspaces when saving images, if palette
    image is required, convert to a ``P`` mode image in the rendering process
    first.



Format Bundle
=============

.. autoclass:: stonemason.formatbundle.FormatBundle
    :members:


Map Writer
==========

.. autoclass:: stonemason.formatbundle.MapWriter
    :members:

.. autoclass:: stonemason.formatbundle.mapwriter.ImageMapWriter
    :members:

