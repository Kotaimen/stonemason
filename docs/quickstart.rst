.. _quickstart:

Quick Start
***********

.. highlight:: console

After you have installed everything using :doc:`install` manual, or, from `pip`,
the `stonemason` CLI should be available as ``stonemason``::

    $ stonemason --version
    Stonemason 0.0.1.dev0

If you prefer to run `stonemason` in "in place" mode, the
package itself is also executable::

    $ cd stonemason
    $ python -m stonemason
    Stonemason 0.0.1.dev0

`stonemason` uses `Click <http://click.pocoo.org>`_ as argument parser, so
getting help is a bit different from other multi command tools like `git`::

    $ stonemason --help
    $ stonemason tileserver --help


Initialize Theme Root
=====================

`stonemason` must have a `theme root` predefined, where all map designs,
render directives, storage configurations are assembled together.

Themes root can be passed as `stonemason` option, or defined in
``STONEMASON_THEMES`` envvar, by default

To init a themes root, use ``init`` command, it will create the directory
structure and configurations for you, with a simple sample theme::

    $ mkdir ~/themes
    $ stonemason --themes=themes init
    Initialization complete, start a tile server using:
        export STONEMASON_THEMES=/home/ubuntu/themes


.. warning:: Because we have not finished map renderer, the init
    command doesn't work out of box, yet.


Configure a Memcache
====================

To start serving tiles, a memcache server is required, the sample theme
generated above requires one listening on local TCP port ``11211``::


    $ telnet localhost 11211
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    stats
    STAT pid 4648
    STAT uptime 1981
    STAT time 1423105263
    STAT version 1.4.20
    ...
    ...
    STAT crawler_reclaimed 0
    END


.. note:: Even if a memcache cluster is used, you can still configure tileserver
    to listen ``localhost:11211`` by using a memcache proxy like
    `Twitter's nutcracker <https://github.com/twitter/twemproxy>`_.



Configure Redis
===============

Redis is used in distributed deployment as message queue, which is not
required in the quickstart.

Tile Server
===========

After created a sample themes root, you can start the tile server::

    $ cd ~/themes
    $ export STONEMASON_THEMES=`pwd`
    $ stonemason --debug n tileserver --bind=127.0.0.1:8000

This starts a `Flask` server with debugging and auto reloading enabled.
To run a production server using `Gunicorn`, remove the ``--debug`` option::

    $ stonemason tileserver --bind=0.0.0.0:8000 --workers=4 --threads=1


TODO: Insert a screenshot here.


Deployment
==========

Here is a sample `Docker` configuration which assumes a dist package in
``dist/`` and themes in ``themes/`` along the ``Dockerfile``:

.. code-block:: Dockerfile

    FROM        ubuntu:trusty
    MAINTAINER  Kotaimen <kotaimen.c@gmail.com>

    ENV         DEBIAN_FRONTEND noninteractive

    ENV         STONEMASON stonemason-0.0.1.dev1
    ENV         STONEMASON_THEMES /opt/stonemason/themes

    WORKDIR     ${STONEMASON_THEMES}

    RUN         apt-get update && \
                apt-get -y install python-dev python-pip && \
                apt-get -y install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev && \
                apt-get -y install libmemcached-dev && \
                apt-get -y install libgeos-dev libgdal-dev gdal-bin python-gdal

    # Speedup slow pip install by caching them first
    RUN         pip install pillow pylibmc

    ADD         dist/${STONEMASON}.tar.gz /tmp/
    RUN         pip install /tmp/${STONEMASON}/

    COPY        themes ${STONEMASON_THEMES}/

    # Check configuration
    RUN         find ${STONEMASON_THEMES}
    RUN         stonemason check

    # Start tile server
    EXPOSE      7086
    CMD         stonemason tileserver --bind 0.0.0.0:7086


If you want to use another ``WSGI`` server or customized `Gunicorn`
configuration, write a ``application.py`` first:

.. code-block:: python

    from stonemason.service.tileserver import TileServerApp
    config = {
        'STONEMASON_THEMES': 'where_themes_root_lies'
    }
    application = TileServerApp(config)

Then point the ``WSGI`` server to ``application.py``::

    $ gunicorn -b 0.0.0.0:7086 application


