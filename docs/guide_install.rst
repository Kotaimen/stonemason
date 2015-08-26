.. _install:

Installation
************

.. highlight:: console

Environment
===========

Due to the complexity of integrating geospatial/imageprocessing/scientific dependencies,
only recent Ubuntu and Homebrew environment are supported.

Binary Packages
===============

Install binary packages first::

     $ sudo apt-get install imagemagick \
     >     python-dev python-pip \
     >     python-scipy python-numpy python-matplotlib cython \
     >     libboost-dev libboost-filesystem-dev libboost-program-options-dev \
     >     libboost-python-dev libboost-regex-dev libboost-system-dev \
     >     libboost-thread-dev \
     >     libz-dev libfreetype6-dev libharfbuzz-dev \
     >     libwebp-dev liblcms2-dev  libjpeg-dev libtiff-dev \
     >     libproj-dev libgeos-dev libgdal-dev gdal-bin python-gdal \
     >     libboost-all-dev libicu-dev \
     >     libfreetype6-dev libsqlite3-dev libpq-dev libxml2-dev \
     >     libmemcached-dev


GEOS/GDAL
~~~~~~~~~

For copyright reasons, `GDAL` debian package don't have some projection
data files included, this requires extra patching form source::

    $ wget http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz
    $ tar x gdal-1.10.1.tar.gz
    $ sudo cp gdal-1.10.1/data/*extra.wkt /usr/share/gdal/1.10/



Mapnik
~~~~~~

For mapnik installation, check check the official installation_ manual.

    .. _installation: <https://github.com/mapnik/mapnik/wiki/UbuntuInstallation>

Mapnik 3 separates python binding from its main repository, and does not support
``pip install mapnik`` yet, so recommended version is still ``2.3 nightly`` branch
on their official repository::

    $ apt-get install -y software-properties-common
    $ add-apt-repository ppa:mapnik/nightly-2.3
    $ apt-get update
    $ apt-get install -y libmapnik libmapnik-dev mapnik-utils python-mapnik \
    >    mapnik-input-plugin-gdal mapnik-input-plugin-ogr \
    >    mapnik-input-plugin-postgis \
    >    mapnik-input-plugin-sqlite \
    >    mapnik-input-plugin-osm


Python Dependency
=================

After grab the source code using Git or source package, run::

    $ pip install -rrequirements.txt
    $ pip install -rrequirements-dev.txt


Build and Test
==============

If you want running `stonemason` without installing you must build all
`Cython` extensions in place::

    $ python setup.py build_ext --inplace

.. warning::

    Cython extension do not work across Python versions, if you compile
    using Python2, they won't work under Python3, you have to clean
    compiled extension first, then rebuild::

        removing 'stonemason/util/geo/_hilbert.'so
        $ python3 setup.py build_ext --inplace --force

`stonemason` uses `nose` for testing::

    $ nosetests
    ...
    ...
    Ran XXX tests in 15.23s
    OK


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



Docker Image
============

A pre-built public docker image is available from docker hub
``kotaimen/stonemason-dev``.