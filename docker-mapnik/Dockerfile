FROM ubuntu:bionic

LABEL MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV DEBIAN_FRONTEND noninteractive

RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN sed -i 's/ports.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN set -eux; \
      apt-get update; \
      apt-get -y --no-install-recommends install \
            locales \
            ca-certificates \
            curl \
            build-essential \
            gcc \
            \
            imagemagick \
            libmapnik3.0 \
            mapnik-utils \
            \
            python3 \
            cython3 \
            python3-pip \
            python3-wheel \
            python3-setuptools \
            python3-dev \
            python3-pil \
            python3-numpy \
            python3-scipy \
            python3-pylibmc \
            python3-skimage \
            python3-gdal \
            python3-mapnik \
            python3-lxml \
            python3-flask \
            python3-click \
            python3-gunicorn \
            python3-requests \
            python3-jinja2 \
            \
            node-carto \
            node-millstone; \
      rm -rf /var/lib/apt/lists/*; \
      locale-gen en_US.UTF-8


ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
