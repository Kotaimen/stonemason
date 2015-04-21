FROM        ubuntu:14.04
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

ENV         STAGE_LOCATION /opt/stonemason/

#
# HACK: Speed local build by using local apt sources
#
# RUN         mv /etc/apt/sources.list /etc/apt/sources.list.back && \
#             sed s/archive.ubuntu.com/mirrors.aliyun.com/ /etc/apt/sources.list.back > /etc/apt/sources.list
# RUN         cat /etc/apt/sources.list

WORKDIR     ${STAGE_LOCATION}

#
# Add ubuntu-gis and mapnik PPA
#
RUN         apt-get update && \
            apt-get -y install software-properties-common && \
            add-apt-repository -y ppa:mapnik/nightly-2.3

#
# Install binary packages
#
RUN         apt-get update &&\
            apt-get -y install python-dev python-pip \
                libz-dev \
                libjpeg-dev libtiff-dev libfreetype6-dev \
                libwebp-dev liblcms2-dev imagemagick \
                libgeos-dev libgdal-dev gdal-bin python-gdal \
                python-mapnik

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
            mapnik-config --version && \
            convert --version && \
            convert rose: /tmp/rose.jpg

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
ADD         http://cdn.masonmaps.me/dist/gdal-1.10.1/data/esri_extra.wkt /usr/share/gdal/1.10/

#
# Install stonemason
#
ADD         . ./
RUN         pip install -rrequirements-dev.txt && \
            pip install .
#
# Check installation
#
RUN         python setup.py build_ext -if
RUN         tox -e py27geo
RUN         stonemason init
RUN         stonemason -v check
