#FROM        kotaimen/stonemason-base:mapnik3.0.9-freetype2.6.3
FROM	    kotaimen/mapnik:3.0.9-ubuntu
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

RUN         locale-gen en_US.UTF-8
ENV         LANG=en_US.UTF-8 \
            LANGUAGE=en_US:en \
            LC_ALL=en_US.UTF-8


#
# Install stonemason and run tests
#

WORKDIR     /tmp/stonemason/

ADD         . ./

RUN         set -x \
                && pip install -rrequirements-dev.txt \
                && pip install . \
                && python setup.py build_ext -i \
                && python -m nose -v \
                && rm -rf /tmp/stonemason

#
# Create a sample at /var/lib/stonemason/map_gallery
#
WORKDIR     /var/lib/stonemason/

RUN         set -x \
                && stonemason init \
                && stonemason check

#
# Entry
#
EXPOSE      80
ENTRYPOINT  ["stonemason"]
CMD         ["tileserver", "--bind=0.0.0.0:80"]
