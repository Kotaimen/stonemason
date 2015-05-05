.. _install:

Installation
************

.. highlight:: console

Environment
===========

Due to the complexity of integrating geospatial packages, using a Python 2.7
interpreter on a Ubuntu distribution is highly recommended.

Binary Packages
===============


.. sidebar:: Tip

    Python3 and packages are all optional.


Install binary packages first:

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

Most geospatial dependencies are optional, only required when component
is actually used.


GEOS/GDAL
~~~~~~~~~

**ubuntu**

Because geospatial libraries already have a very large dependency tree, its 
highly recommended install them from system package manager::

    $ sudo apt-get install libgeos-dev
    $ sudo apt-get install python-scipy python-numpy
    $ sudo apt-get install gdal-bin python-gdal
    $ sudo apt-get install python3-scipy python3-numpy
    $ sudo apt-get install python3-gdal

.. note:: Its important to install `scipy`/`numpy` first, otherwise `python-gdal`
    won't install `numpy` bindings properly. `stonemason` uses it in the custom
    relief shading renderer.

`ubuntu-14.04-LTS` comes with reasonably recent `GEOS` and `GDAL`, for
older ubuntu versions, install from `ubuntu-gis` PPA is recommended::

    $ sudo apt-get install -qq python-software-properties
    $ sudo add-apt-repository -y ppa:ubuntugis/ppa
    $ sudo apt-get update
    $ sudo apt-get install libgeos-dev gdal-bin python-gdal

For copyright reasons, `GDAL` debian package don't have some projection
data files included, this requires extra patching form source::

    $ wget http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz
    $ tar x gdal-1.10.1.tar.gz
    $ sudo cp gdal-1.10.1/data/*extra.wkt /usr/share/gdal/1.10/


**Mac**

    $ pip install numpy scipy
    $ brew install geos gdal

Mapnik
~~~~~~

At the time of writing, the stable `mapnik` version is still ``2.2.0``, it comes
with `ubuntu-14.04-LTS` and can be installed from system package manager::

    $ apt-get install python-mapnik

To install the latest nightly ``2.3.x`` branch or ``3.0.0-pre`` branch, check
the official installation_ manual.

    .. _installation: <https://github.com/mapnik/mapnik/wiki/UbuntuInstallation>

For rendering OSM or large maps, compiling the PostGIS plugin and use it as
data source is highly recommended.

Installing from mapnik official ubuntu repository::

    $ apt-get install -y software-properties-common
    $ add-apt-repository ppa:mapnik/nightly-2.3
    $ apt-get update
    $ apt-get install -y libmapnik libmapnik-dev mapnik-utils python-mapnik \
        mapnik-input-plugin-gdal mapnik-input-plugin-ogr \
        mapnik-input-plugin-postgis \
        mapnik-input-plugin-sqlite \
        mapnik-input-plugin-osm



Python Dependency
=================

After grab the source code using Git or source package, run::

    $ pip3 install -rrequirements.txt
    $ pip3 install -rrequirements-dev.txt

    $ pip install -rrequirements.txt
    $ pip install -rrequirements-dev.txt


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

        removing 'stonemason/util/geo/_hilbert.'so
        $ python3 setup.py build_ext --inplace --force

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
      py27geo: commands succeeded
      py34: commands succeeded
      docs: commands succeeded
      congratulations :)


.. note::  The test suites expects a memcached server listens on localhost
    TCP 11121 port.


Document
========

Build html based document::

    $ cd docs
    $ make html

To build PDF version `textlive` is required::

    $ sudo apt-get install texlive texlive-latex-extra
    $ make latexpdf


