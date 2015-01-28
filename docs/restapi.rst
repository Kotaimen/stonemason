Tile Map Service
================

*TMS* (Tile Map Service).


Retrieve Theme Info
-------------------

::

    GET /themes/:theme

Parameters:

===================  ======================================
Name                 Description
===================  ======================================
``:theme``           Name of the theme, *required*.
===================  ======================================


Response:

::

    Status: 200 OK

.. code-block:: javascript

    {
        "name": "stingray",
        "description": "A flat fish related to sharks",
        "levels": [1, 2, 3, 4, 5, 6, 7, 8]
    }
