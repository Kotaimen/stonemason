FROM        kotaimen/stonemason-base:mapnik3
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# Install stonemason and run tests
#

WORKDIR     /tmp/stonemason/

ADD         . ./

RUN         set -x \
                && pip3 install -rrequirements-dev.txt \
                && pip3 install . \
                && python3.5 setup.py build_ext -i \
                && python3.5 -m nose \
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
CMD         [tileserver", "--bind=0.0.0.0:80"]
