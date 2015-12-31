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

     $ sudo apt-get install install
     >          python-dev \
     >          python-pip \
     >          libmemcachd-dev \
     >          libgdal-dev \
     >          python-gdal \
     >          imagemagick \
     >          libwebp-dev \
     >          libpng-dev \
     >          libjpeg-dev \
     >          libtiff-dev

GEOS/GDAL
~~~~~~~~~

For copyright reasons, `GDAL` debian package don't have some projection
data files included, this requires extra patching form source::

    $ wget http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz
    $ tar x gdal-1.10.1.tar.gz
    $ sudo cp gdal-1.10.1/data/*extra.wkt /usr/share/gdal/1.10/


Mapnik
~~~~~~

For ``mapnik``, check their official installation_ manual.

    .. _installation: <https://github.com/mapnik/mapnik/wiki/UbuntuInstallation>

At the time of writing they provide pip distribution for python2.7 on
debian/homebrew enviroment::

    $ pip install mapnik


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

A docker image with all dependencies installed is provided which can be used
to quickly build a sample tile map service::

    $ docker run -p 0.0.0.0:80:80 kotaimen/stonemason
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Starting gunicorn 19.2.1
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Listening at: http://0.0.0.0:7086 (43027)
    [2015-03-02 18:10:00 +0800] [43027] [INFO] Using worker: threads
    [2015-03-02 18:10:00 +0800] [43054] [INFO] Booting worker with pid: 43054

