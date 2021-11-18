ARG UBUNTU_VERSION=bionic

FROM ubuntu:${UBUNTU_VERSION} AS stonemason-build

ARG UBUNTU_ARCHIVE=mirrors.aliyun.com
ARG UBUNTU_PORTS=mirrors.aliyun.com

ENV DEBIAN_FRONTEND noninteractive

RUN sed -i s/archive.ubuntu.com/${UBUNTU_ARCHIVE}/g /etc/apt/sources.list
RUN sed -i s/ports.ubuntu.com/${UBUNTU_PORTS}/g /etc/apt/sources.list

RUN set -eux; \
      apt-get update; \
      apt-get -y install \
            python3-dev \
            python3-wheel \
            python3-setuptools \
            cython3

WORKDIR /build
ADD . ./
RUN set -eux; \
    python3 setup.py build; \
    python3 setup.py bdist_wheel


FROM ubuntu:${UBUNTU_VERSION} AS mapnik-base

ARG UBUNTU_ARCHIVE=mirrors.aliyun.com
ARG UBUNTU_PORTS=mirrors.aliyun.com

ENV DEBIAN_FRONTEND noninteractive

RUN sed -i s/archive.ubuntu.com/${UBUNTU_ARCHIVE}/g /etc/apt/sources.list
RUN sed -i s/ports.ubuntu.com/${UBUNTU_PORTS}/g /etc/apt/sources.list

RUN set -eux; \
      apt-get update; \
      apt-get -y --no-install-recommends install \
            locales \
            ca-certificates \
            curl \
            \
            imagemagick \
            libmapnik3.0 \
            mapnik-utils \
            \
            python3 \
            python3-pip \
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
            \
      pip3 install  \
            boto3; \
      rm -rf /var/lib/apt/lists/*; \
      locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8


FROM mapnik-base AS stonemason

# Install stonemason
WORKDIR /tmp/workdir
COPY --from=stonemason-build /build/dist/*.whl ./
RUN set -eux; \
  ls ; \
  pip3 install *.whl; \
  rm -rf *

# Create a sample at /var/lib/stonemason/map_gallery
WORKDIR /var/lib/stonemason/
RUN set -eux; \
  stonemason init; \
  stonemason check

# Entry
EXPOSE 80
ENTRYPOINT ["stonemason"]
CMD ["tileserver", "--bind=0.0.0.0:80"]
