FROM        ubuntu:14.04
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

ENV         STAGE_LOCATION /opt/stonemason/

#
# HACK: Speed local build by using local apt sources
#
#RUN         mv /etc/apt/sources.list /etc/apt/sources.list.back
#RUN         sed s/archive.ubuntu.com/ap-northeast-1.ec2.archive.ubuntu.com/ /etc/apt/sources.list.back > /etc/apt/sources.list
#RUN         cat /etc/apt/sources.list

WORKDIR     ${STAGE_LOCATION}

#
# Common package dependencies
#
RUN         apt-get update
RUN         apt-get -y install python-dev python-pip
RUN         apt-get -y install libjpeg-dev libz-dev libtiff-dev libfreetype6-dev libwebp-dev liblcms2-dev
RUN         apt-get -y install imagemagick

#
# Speedup pip install by install "must have" prerequests first
#
RUN         pip install pillow flask boto gunicorn six Click python-memcached
RUN         pip install nose coverage tox Cython Pygments alabaster Sphinx sphinxcontrib-httpdomain moto

#
# Add ubuntu-gis and mapnik PPA
#
RUN         apt-get -y install software-properties-common
RUN         add-apt-repository -y ppa:mapnik/nightly-2.3
RUN         apt-get update

#
# Install geos/gdal/mapnik
#
RUN         apt-get -y install libgeos-dev libgdal-dev gdal-bin python-gdal
RUN         apt-get -y install python-mapnik

#
# Check installed software
#
RUN         geos-config --version
RUN         ogrinfo --version
RUN         mapnik-config --version
RUN         convert --version
RUN         convert rose: /tmp/rose.jpg

#
# Set the locale otherwise Click will complain,
# See http://click.pocoo.org/3/python3/
RUN         locale-gen en_US.UTF-8
ENV         LANG en_US.UTF-8
ENV         LANGUAGE en_US:en
ENV         LC_ALL en_US.UTF-8

#
# Patch gdal data files, see
#   https://launchpad.net/ubuntu/trusty/+source/gdal/+copyright
# Download gdal source packages from 
#   http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz
ADD         gdal-1.10.1.tar.gz /tmp/
RUN         ls /usr/share/gdal
RUN         cp /tmp/gdal-1.10.1/data/*extra.wkt /usr/share/gdal/1.10/

#
# Install stonemason
#
ADD         . ./
RUN         pip install -rrequirements-dev.txt
RUN         pip install .
RUN         python setup.py build_ext -if
RUN         tox -e py27geo

#
# Start the sample theme tile server
#
EXPOSE      8080
RUN         stonemason init
RUN         stonemason check
CMD         stonemason -dd tileserver -b 0.0.0.0:8080
