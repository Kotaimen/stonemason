Map Format
**********

.. module::stonemason.provider.formatbundle

:mod:`stonemason.provider.formatbundle` defines map types, tile formats and
their conversions.

.. warning:: Contents of this package is subject to change when dynamic
    format registering is implemented.

Map Type
========

.. autoclass:: stonemason.provider.formatbundle.MapType
    :members:

Tile Format
===========

.. autoclass:: stonemason.provider.formatbundle.TileFormat
    :members:

Common Formats
--------------

See `pillow file formats <https://pillow.readthedocs.org/handbook/image-file-formats.html>`_
for a complete list of image format parameters.

.. note:: Many these formats require `pillow` to compiled with proper
     drivers.  For tile map images, specify ``quality`` and ``optimized``
     parameters is usually sufficient.

.. note:: `Pillow` don't convert colorspaces when saving images, if palette
    image is required, convert to a ``P`` mode image in the rendering process
    first.


=======  ============= =========
Format   Mimetype      Extension
=======  ============= =========
JPEG     image/jpeg    .jpg
PNG      image/png     .png
=======  ============= =========

Format Bundle
=============

.. autoclass:: stonemason.provider.formatbundle.FormatBundle
    :members:


Map Writer
==========

.. autoclass:: stonemason.provider.formatbundle.MapWriter
    :members:

.. autoclass:: stonemason.provider.formatbundle.mapwriter.ImageMapWriter
    :members:

