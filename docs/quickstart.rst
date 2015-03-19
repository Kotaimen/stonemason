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

Themes root can be passed as ``--themes`` option, or defined in
``STONEMASON_THEMES`` envvar.

To init a themes root, use ``init`` command, it will create the directory
structure and configurations for you, with a simple sample theme::

    $ mkdir ~/themes
    $ stonemason --themes=themes init
    Initialization complete, start a tile server using:
        export STONEMASON_THEMES=/home/ubuntu/themes


.. warning:: Because we have not finished map renderer, the init
    command doesn't work out of box, yet.

Check Theme Configuration
=========================

To verify theme configuration, use ``check`` subcommand:

    $ stonemason --themes=themes -v check

Configure a Memcache
====================


.. sidebar:: Tip

    Even if a memcache cluster is used, you can still configure tileserver
    to listen ``localhost:11211`` by using a memcache proxy like
    `Twitter's nutcracker <https://github.com/twitter/twemproxy>`_.


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


Configure Redis
===============

Redis is used in distributed deployment as message queue, which is not
required in the quickstart.

Tile Server
===========

After created a sample themes root, you can start the tile server::

    $ cd ~/themes
    $ export STONEMASON_THEMES=`pwd`
    $ stonemason -dd tileserver --bind=127.0.0.1:8000

The ``-dd`` option means a debugging flask server will be started, to start
To production server using `Gunicorn`, don't supply the ``--debug`` option::

    $ stonemason tileserver --bind=0.0.0.0:8000
    [2015-03-02 18:09:30 +0800] [42985] [INFO] Starting gunicorn 19.2.1
    [2015-03-02 18:09:30 +0800] [42985] [INFO] Listening at: http://127.0.0.1:7086 (42985)
    [2015-03-02 18:09:30 +0800] [42985] [INFO] Using worker: sync
    [2015-03-02 18:09:30 +0800] [43013] [INFO] Booting worker with pid: 43013
    [2015-03-02 18:09:31 +0800] [43014] [INFO] Booting worker with pid: 43014


When `Gunicorn` server is used, you can specify number of worker processes used
and number of threads per worker::

    $ stonemason tileserver --bind=0.0.0.0:8000 --workers=2 --threads=4
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Starting gunicorn 19.2.1
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Listening at: http://127.0.0.1:7086 (43027)
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Using worker: threads
    [2015-03-02 18:10:00 +0800] [43054] [INFO] Booting worker with pid: 43054
    [2015-03-02 18:10:00 +0800] [43055] [INFO] Booting worker with pid: 43055

If you have `memcache` server configured above, use it to speedup::

    $ stonemason tileserver --bind=0.0.0.0:8000 --workers=2 --threads=4 --cache=localhost:11211

Or define it in envvar ``STONEMASON_CACHE``::

    $ export STONEMASON_CACHE=localhost:11211

If a memcache cluster is used, separate each node with ``;`` or space::

    $ export STONEMASON_CACHE=10.0.16.1:11211;10.0.16.2:11211

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

    WORKDIR     ${STONEMASON_THEMES}

    RUN         apt-get update && \
                apt-get -y install python-dev python-pip && \
                apt-get -y install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev

    # Set the locale otherwise Click will complain,
    # See http://click.pocoo.org/3/python3/
    RUN         locale-gen en_US.UTF-8
    ENV         LANG en_US.UTF-8
    ENV         LANGUAGE en_US:en
    ENV         LC_ALL en_US.UTF-8

    # Speedup pip install by install "must have" prerequests first
    RUN         pip install pillow flask boto gunicorn six Click

    ADD         dist/${STONEMASON}.tar.gz /tmp/
    RUN         pip install /tmp/${STONEMASON}/

    COPY        themes ${STONEMASON_THEMES}/

    # Install stonemason
    ADD         dist/${STONEMASON}.tar.gz /tmp/
    RUN         pip install /tmp/${STONEMASON}/

    COPY        themes ${STONEMASON_THEMES}/

    # Check configuration
    RUN         find ${STONEMASON_THEMES}
    RUN         stonemason -v check

    # Start tile server
    EXPOSE      7086
    CMD         stonemason tileserver --bind 0.0.0.0:7086

To start tileserver in docker container, use::

    $ docker build -t stonemason .
    $ docker run -p 0.0.0.0:7086:7086 stonemason stonemason tileserver --bind 0.0.0.0:7086 --workers=1
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Starting gunicorn 19.2.1
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Listening at: http://127.0.0.1:7086 (43027)
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Using worker: threads
    [2015-03-02 18:10:00 +0800] [43054] [INFO] Booting worker with pid: 43054


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


