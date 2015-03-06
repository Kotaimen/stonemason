.. _install:

.. highlight:: console

Installation
************

Python2 or Python3?
===================

Being a cartography package, `stonemason` has lots of binary and Python
geospatial package dependencies.  Although `stonemason` works on both
Python2 and Python3, some binary packages (like `gdal`) still don't have
a Python3 plugin.

`stonemason` is carefully designed so components have geospatial dependency
(eg: the `mapnik` renderer) and components which don't have (eg: the tile
server) are separated.  Thus a distributed deployment don't require install
geospaial packages on all nodes.

However, in a "all-in-one" develop environment, you still have to install
every dependency and stick with Python2.

`stonemason` is developed and tested against Python 2.7 and Python 3.4.
Develop is done on Mac homebrew, deploying to `ubuntu-14.04-LTS` and
`ubuntu-12.04-LTS` when the latest version is not available.


Binary Packages
===============

Install following binary packages first.

.. note:: If you only planning use Python2, you don't need have all the python3
    stuff installed.

**ubuntu**

First, install Python::

    $ sudo apt-get install python-dev python-pip
    $ sudo apt-get install python3-dev python3-pip


Install packages for PIL/Pillow::

    $ sudo apt-get install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev

Install memcache::

    $ sudo apt-get install memcached libmemcached-dev

**Mac**

On MacOS, use `homebrew <http://brew.sh/>`_ to install binary packages::

    $ brew install python python3
    $ brew install libjpeg libz libtiff freetype libwebp lcms2
    $ brew install memcached libmemcached

Optional Packages
=================

Optional packages are required when rendering maps.

GEOS/GDAL
~~~~~~~~~

**ubuntu**

Because geospatial libraries already have a very large dependency tree, its 
highly recommended install them from system package manager::

    $ sudo apt-get install libgeos-dev
    $ sudo apt-get install python-scipy python-numpy
    $ sudo apt-get gdal-bin python-gdal
    
.. note:: Its important to install `scipy`/`numpy` first, otherwise `python-gdal`
    won't install `numpy` bindings properly. `stonemason` uses it in the custom
    relief shading renderer.

`ubuntu-14.04-LTS` comes with reasonably recent `geos` and `gdal`, for
older ubuntu versions, install from `ubuntu-gis` is recommended::

    $ apt-get install -qq python-software-properties
    $ add-apt-repository -y ppa:ubuntugis/ppa
    $ apt-get update
    $ apt-get install libgeos-dev gdal-bin python-gdal

**Mac**

**TODO**

Mapnik
~~~~~~

At the time of writing, the stable `mapnik` version is still ``2.2.x``, it comes
with `ubuntu-14.04-LTS` and can be installed from system package manager::

    $ apt-get install python-mapnik

To install the latest nightly ``2.3.x`` branch or ``3.0.0-pre`` branch, check
the offical installation_ manual.

Recommend `mapnik` version is latest ``2.3.x`` branch, which contains a lots
of new features and fixes without breaking xml stylesheet, much.

    .. _ubuntuinstallation: <https://github.com/mapnik/mapnik/wiki/UbuntuInstallation>


Python Dependency
=================

After grab the source code using Git or source package, run::

    $ pip install -rrequirements.txt
    $ pip install -rrequirements-dev.txt

    $ pip3 install -rrequirements.txt
    $ pip3 install -rrequirements-dev.txt


Virtualenv
==========

If you only plan using `stonemason` to render/serve maps, its recommended
to install it into a virtualenv using `pip`.

Because most binary dependency's Python binding are installed to system python,
the virtualenv also need to include system ``site-package``::

    $ pip install virtualenv
    $ mkdir ~/www/stonemason
    $ virtualenv ~/www/stonemason --system-site-packages
    $ source ~/www/stonemason/bin/activate

After activated virtualenv, your shell prompt will change to ``(stonemason)$``::

    (stonemason)$ cd ~/proj/stonemason
    (stonemason)$ pip install .
    ...
    ...
    Successfully installed stonemason
    Cleaning up...

To quit the virtual environment, use::

    (stonemason)$ deactivate
    $


Build and Test
==============

If you want running `stonemason` without installing you must build all
`Cython` extensions in place::

    $ python setup.py build_ext --inplace

Or use Python3::

    $ python3 setup.py build_ext --inplace

.. warning::

    Cython extension do not work across Python versions, if you compile
    using Python2, they won't work under Python3, you have to clean
    compiled extension first, then rebuild::

        $ python setup.py clean
        running clean
        removing 'build/temp.macosx-10.10-x86_64-2.7' (and everything under it)
        removing 'stonemason/util/geo/_hilbert.'c
        removing 'stonemason/util/geo/_hilbert.'so
        $ python3 setup.py build_ext --inplace

`stonemason` uses `nose` and `tox` for testing::

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


.. note::  The test suites expects a memcached server listens on localhost
    TCP 11121 port.


Document
========

::

    $ cd docs
    $ make html


