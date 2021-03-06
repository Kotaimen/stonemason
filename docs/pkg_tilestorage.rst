Tile Storage
************

.. module:: stonemsaon.provider.tilestorage

Implements persistent tile storage.  For performance and cost reasons, only
`MetaTile`s and `TileClusters` can be placed in the storage. There are two
types of storage:

    :class:`~stonemason.tilestorage.ClusterStorage`
        stores a cluster of tiles as zipped file.

    :class:`~stonemason.tilestorage.MetaTileStorage`
        stores raw, uncropped metatile data.

A MetaTileStorage can be converted to a read only ClusterStorage using a
:class:`~stonemason.tilestorage.Clusterfier`, but not vise versa.

Currently there are two types of storage backends:

    `disk`
        Local filesystem.

    `s3`
        AWS Simple Storage Service.

More backends will be added in the future.


Exceptions
==========

Tile Cluster
============

.. autoclass:: stonemason.pyramid.TileCluster
    :members: __getitem__

Cluster File Format
===================

`TileCluster` is stored as a `zip` file, zip format is chosen because
there is no easy way to read a tar.gz file on non `*nix` platforms.

A cluster zip file contains following files::

    z-x-y@stride.zip
    +-+
      |- index.json
      |- z1-x1-y1.ext
       ...
      |- z2-x2-y2.ext

`z-x-y.ext` is the tile data, ``index.json`` describes the contents in
the zip file:

.. code-block:: javascript

    {
        "version": 1,
        "datas": [
            "1-0-0",
            "1-1-1"
            ],
        "tiles": {
            "1-0-0": "1-0-0",
            "1-0-1": "1-0-0",
            "1-1-0": "1-0-0",
            "1-1-1": "1-1-1"
            },
        "stride": 4,
        "extension": ".png",
        "mimetype": application/data,
        "mtime": 1421857314.309366,
        "etag": "d41d8cd98f00b204e9800998ecf8427e"
    }

JSON fields:

    `version`

        Version of the index.json, always ``1`` at the time of writing.

    `datas`

        A list of tile data file name with out extension in ``z-x-y`` format.

    `tiles`

        A mapping of ``(tile_index, tile_data)``, multiple indexes can point
        to same tile data if they are identical.

    `extension`

        File extension of the tile data, with the starting ``.``, the
        extension is guessed from `mimetype`.

    `stride`

        Optional, stride of the metatile.

    `mimetype`

        Optional, mimetype of the metatile.

    `mtime`

        Optional, last modified time of the metattile.


.. note::

    Optional fields are designed to work with legacy renders, current
    cluster will always write these fields.

