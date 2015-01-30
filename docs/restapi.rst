Tile Map Service
================

*TMS* (Tile Map Service).


Retrieve Theme Info
-------------------

.. http:get:: /themes/(theme)

    Get information of a theme with its name.

    **Example request**:

        .. code-block:: http

            GET /themes/stingray HTTP/1.1
            Host: example.com
            Accept: application/json, text/javascript

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-type: application/json
            Cache-Control: public, max-age=300

            {
                "name": "stingray",
                "description": "A flat fish related to sharks",
                "levels": [1, 2, 3, 4, 5, 6, 7, 8]
            }

    :param theme: name of the theme, *required*.

    :resheader Content-Type: a json object describes metadata of a theme.
    :resheader Cache-Control: default max age is 300 seconds.

    :status 200: No error.
    :status 404: when theme doesn't exist.
    :status 400: when request is not valid.


List Theme Info
---------------

.. http:get:: /themes

    List brief of all the themes on the server.

    **Example request**:

        .. code-block:: http

            GET /themes HTTP/1.1
            Host: example.com
            Accept: application/json, text/javascript

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-type: application/json
            Cache-Control: public, max-age=300

            [
                {
                    "name": "indigo",
                    "description": "What a wonderful world.",
                    "projection": "EPSG:3857",
                    "levels": [1, 2, 3, 4, 5, 6, 7, 8]
                },
                {
                    "name": "mustard",
                    "description": "Tastes great.",
                    "projection": "EPSG:3857",
                    "levels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                }
            ]

    :resheader Content-Type: a json object contains list of theme metadata.
    :resheader Cache-Control: default max age is 300 seconds.

    :status 200: no error.
    :status 400: when request is not valid.


Retrieve Tile
-------------

.. http:get:: /tile/(tag)/(int:z)/(int:x)/(int:y).(ext)

    Get a tile with a theme tag, a zoom level and  a (x, y) coordinate.


    **Example request**:

        .. code-block:: http

            GET /brick/0/0/0.png HTTP/1.1
            Host: example.com
            Accept: image/png, image/jpeg, image/geojson

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-type: image/png
            Cache-Control: public, max-age=86400
            Etag: a00049ba79152d03380c34652f2cb612
            Last-Modified: Sat, 27 Apr 2015 00:44:54 GMT

            Image Data

    :param tag: tag of the theme, *required*.
    :param z: zoom level, *required*.
    :type z: int
    :param x: x coordinate, *required*.
    :type x: int
    :param y: y coordinate, *required*.
    :type y: int
    :param ext: tile format, could be png, jpeg, jpg, geojson, *required*.

    :resheader Content-Type: image format of a tile.
    :resheader Cache-Control: default max age is 86400 seconds.
    :resheader ETag: unique identifier for a tile.
    :resheader Last-Modified: modified time of a tile.

    :status 200: no error.
    :status 404: when tile not found.
    :status 400: when request is not valid.
