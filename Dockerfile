FROM        ubuntu:14.04
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# HACK: Speed local build by using local apt sources
#
# RUN         mv /etc/apt/sources.list /etc/apt/sources.list.back && \
#             sed s/archive.ubuntu.com/mirrors.aliyun.com/ /etc/apt/sources.list.back > /etc/apt/sources.list
# RUN         cat /etc/apt/sources.list


#
# Install binary packages
#
RUN         apt-get update &&\
            apt-get -y install python-dev python-pip \
                libz-dev unzip\
                libjpeg-dev libtiff-dev libfreetype6-dev \
                libwebp-dev liblcms2-dev imagemagick \
                libproj-dev libgeos-dev libgdal-dev gdal-bin python-gdal \
                libboost-all-dev libicu-dev \
                libfreetype6-dev libsqlite3-dev libpq-dev libcairo-dev

#
# Install mapnik
#

# XXX: Cheat by using our ready-to-install package, mapnik takes forever to build...
WORKDIR     /tmp/
ADD         http://cdn.masonmaps.me/dist/ubuntu-14.04/mapnik-2.3.x.tar.gz ./
RUN         tar xf mapnik-2.3.x.tar.gz
WORKDIR     /tmp/mapnik-2.3.x
RUN         make install

#
# Speedup pip by install "must have" python packages first
#
RUN         pip install \
                pillow flask boto gunicorn six Click python-memcached \
                nose coverage tox Cython Pygments alabaster \
                Sphinx sphinxcontrib-httpdomain moto

#
# Check installed software
#
RUN         geos-config --version && \
            ogrinfo --version && \
            ogrinfo --formats && \
            mapnik-config --version && \
            ls `python -c 'import mapnik; print mapnik.inputpluginspath'` && \
            convert --version && \
            convert rose: /tmp/rose.jpg && \
            convert rose: /tmp/rose.png && \
            convert rose: /tmp/rose.tiff && \
            convert rose: /tmp/rose.webo

#
# Set locale, otherwise Click complains, see http://click.pocoo.org/3/python3/
#
RUN         locale-gen en_US.UTF-8
ENV         LANG en_US.UTF-8
ENV         LANGUAGE en_US:en
ENV         LC_ALL en_US.UTF-8

#
# Patch gdal data files, see
#   https://launchpad.net/ubuntu/trusty/+source/gdal/+copyright
ADD         http://cdn.masonmaps.me/dist/ubuntu-14.04/gdal-1.10.1/data/esri_extra.wkt /usr/share/gdal/1.10/

#
# Install stonemason
#

WORKDIR     /tmp/stonemason
ADD         . ./
RUN         pip install -rrequirements-dev.txt && \
            pip install .
#
# Check installation
#
RUN         python setup.py build_ext -if
RUN         tox -e py27geo
RUN         stonemason init
RUN         stonemason check

RUN         rm -rf /tmp/stonemason && \
            rm -rf /tmp/mapnik-2.3.x && \
            rm /tmp/rose*
