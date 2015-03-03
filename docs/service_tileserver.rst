Tile Map Service
****************

*TMS(Tile Map Service) REST API*


Theme API
=========

A list of HTTP REST APIs used to retrieve and list themes.

Retrieve Theme
--------------

.. http:get:: /themes/(tag)

    Get information of a theme with its tag.

    **Example request**:

        .. code-block:: http

            GET /themes/stingray HTTP/1.1
            Host: example.com
            Accept: application/json, text/javascript

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Cache-Control: public, max-age=300

            {
                "name": "stingray",
                "description": "A flat fish related to sharks",
                "levels": [1, 2, 3, 4, 5, 6, 7, 8]
            }

    :param tag: Name of the theme, *required*.
    :type tag: str

    :resheader Content-Type: A json object describes metadata of a theme.
    :resheader Cache-Control: Default max age is 300 seconds.

    :status 200: No error.
    :status 404: When theme doesn't exist.
    :status 400: When request is not valid.


List Theme
----------

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
            Content-Type: application/json
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

    :resheader Content-Type: A json object contains list of theme metadata.
    :resheader Cache-Control: Default max age is 300 seconds.

    :status 200: No error.
    :status 400: When request is not valid.


Tile API
========

A list of HTTP REST APIs used to retrieve tiles.

Retrieve Tile
-------------

.. http:get:: /tiles/(tag)/(int:z)/(int:x)/(int:y)@(scale).(ext)

    Get a tile with a theme tag, a zoom level and  a (x, y) coordinate.


    **Example request**:

        .. code-block:: http

            GET /brick/0/0/0@2x.png HTTP/1.1
            Host: example.com
            Accept: image/png, image/jpeg, image/geojson

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: image/png
            Cache-Control: public, max-age=86400
            Etag: a00049ba79152d03380c34652f2cb612
            Last-Modified: Sat, 27 Apr 2015 00:44:54 GMT

            Image Data

    :param tag: Tag of the theme, *required*.
    :type tag: str
    :param z: Zoom level, *required*.
    :type z: int
    :param x: The x coordinate, *required*.
    :type x: int
    :param y: The y coordinate, *required*.
    :type y: int
    :param scale: Scale Factor, *required*.
    :type scale: str
    :param ext: Tile format, could be png, jpeg, jpg, geojson, *required*.
    :type ext: str

    :resheader Content-Type: Image format of a tile.
    :resheader Cache-Control: Default max age is 86400 seconds.
    :resheader ETag: Unique identifier for a tile.
    :resheader Last-Modified: Modified time of a tile.

    :status 200: No error.
    :status 404: When tile not found.
    :status 400: When request is not valid.

.. http:get:: /tiles/(tag)/(int:z)/(int:x)/(int:y).(ext)

    Short way for retrieving a tile of scale 1.


Map API
=======

A list of HTTP REST APIs used to retrieve maps.

Retrieve Map
------------

.. http:get:: /maps/(tag)

    Get a Map with the given tag.

    **Example request**:

        .. code-block:: http

            GET /maps/brick HTTP/1.1
            Host: example.com
            Accept: */*

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: text/html
            Cache-Control: private, max-age=0

            <!DOCTYPE html>
            <html>
            ...
            </html>

    :param tag: Tag of the theme, *required*.
    :type tag: str

    :resheader Content-Type: Map of the specified tag.
    :resheader Cache-Control: Default max age is 0 seconds.

    :status 200: No error.
    :status 404: No such map.


Status API
==========

A list of HTTP REST APIs used to get status of tile server.

Health Check
------------

.. http:get:: /health_check

    Check availability of the tile server.

    **Example request**:

        .. code-block:: http

            GET /health_check HTTP/1.1
            Host: example.com
            Accept: */*

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: text/plain
            Cache-Control: private, max-age=0

    :resheader Content-Type: Plain text.
    :resheader Cache-Control: Do not cache.

    :status 200: No error.


Admin API
=========

A map management console.

Overview
--------

.. http:get:: /

    Return the management console of the tile server.

    **Example request**:

        .. code-block:: http

            GET / HTTP/1.1
            Host: example.com
            Accept: */*

    **Example response**:

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: text/html

    :resheader Content-Type: HTML page.

    :status 200: No error.
