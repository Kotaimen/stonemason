.. _quickstart:

Quick Start
===========

.. highlight:: console

After you have installed everything using :doc:`install` manual, or, from `pip`,
the `stonemason` CLI should be available as ``stonemason``::

    $ stonemason --version
    Stonemason 0.0.1.dev0

If you prefer to run `stonemason` in "in place" mode, the
package itself is executable::

    $ cd stonemason
    $ python -m stonemason
    Stonemason 0.0.1.dev0


Initialize Theme Root
---------------------

`stonemason` must have a theme root predefined, where all map designs,
render directives, storage configurations are assembled together.

Themes root can be passed as `stonemason` option, or defined in
``STONEMASON_THEMES`` envvar.

To init a themes root, use ``init`` command, it will ask a few questions
then create the directory structure and configurations for you::

    $ mkdir ~/themes
    $ cd ~/themes
    $ stonemason --themes=. init
    Initializing themes root at ~/themes ...


    ..note:: Currently, only themes type supported is a local directory.


Configure a Memcache
--------------------

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


.. tip:: Even if a memcache cluster is used, you can still configure tileserver
    to ``localhost:11211`` by using a memcache proxy like
    `Twitter's nutcracker <https://github.com/twitter/twemproxy>`_.



Configure Redis
---------------

Redis is used in distributed deployment as message queue, which is not
required in the quickstart.

Tile Server
-----------

After created a sample themes root, you can start a tile server::

    $ cd ~/themes
    $ export STONEMASON_THEMES=`pwd`
    $ stonemason tileserver start --bind=127.0.0.1:8000
    Stonemason tileserver serving from ~/themes


TODO: Insert a screenshot here.


Deployment
----------

TODO: Explain nginx + gunicorn + application.py here.
