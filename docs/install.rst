Installation
============

Python2 or Python3?
-------------------

Being a cartography package, `stonemason` has lots of binary and Python
geospatial package dependencies.  Although stonemason itself works on
both Python2 and Python3, some packages (like `gdal`) still don't have
a Python3 plugin.

To solve this issue, we separated components that has geospatial
dependency (eg: the `mapnik` renderer) and components which doesn't
(eg: the tile server), so a distributed deployment don't require
install geospaial packages on all nodes.

However, on a "all-in-one" installation and development environment,
you still have to install every dependency and stick with Python2.7.


The All-In-One Way
------------------

(And develop environment)

Because geospatial libraries like `geos`/`gdal` and `mapnik` already have
a very large dependency tree, its highly recommended install them from
system package manager.


Binary Packages
~~~~~~~~~~~~~~~

.. highlight:: console

**ubuntu-14.04-LTS**

First, install Python, note if you only planning using Python2, you don't need
have python3 stuff installed::

    $ apt-get install python-dev python-pip
    $ apt-get install python3-dev python3-pip


Install packages for PIL/Pillow::

    $ apt-get install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev

Install memcache::

    $ apt-get install memcached libmemcached-dev

**Mac**

On MacOS, use `homebrew <http://brew.sh/>`_ to install binary packages::

    $ brew install python python3
    $ brew install libjpeg libz libtiff freetype libwebp lcms2
    $ brew install memcached libmemcached


Python Dependency
~~~~~~~~~~~~~~~~~

After grab the source code using Git or source package, run::

    $ pip install -rrequirements.txt
    $ pip3 install -rrequirements.txt

For developers or building documents, also install development requirements::

    $ pip install -rrequirements-dev.txt
    $ pip3 install -rrequirements-dev.txt


GEOS and GDAL
~~~~~~~~~~~~~

TODO

Mapnik
~~~~~~

TODO

Imagemagick
~~~~~~~~~~~

TODO


Build and Test
--------------

If you want running in-place you must build `Cython` extensions in place::


    $ python setup.py build_ext --inplace

Or use Python3::

    $ python3 setup.py build_ext --inplace

Otherwise, install stonemason into Python site packages::

    $ python setup.py install


.. note::

    Cython extension do not work across Python versions, if you compile
    using Python2, they won't work under Python3, you have to clean
    compiled extension first, then rebuild::

        $ python setup.py clean
        running clean
        removing 'build/temp.macosx-10.10-x86_64-2.7' (and everything under it)
        removing 'stonemason/util/geo/_hilbert.'c
        removing 'stonemason/util/geo/_hilbert.'so
        $ python3 setup.py build_ext --inplace


`stonemason uses `nose` and `tox` for testing::

    $ nosetests
    ...
    ...
    Ran XXX tests in 15.23s
    OK
    $ tox
    ...
    ...
    ____________________________ summary _____________________________
      py27: commands succeeded
      py34: commands succeeded
      docs: commands succeeded
      congratulations :)


Document
--------

To build sphinx documents::

    $ cd docs
    $ make html

