FROM        kotaimen/stonemason-base
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# Install stonemason and run tests
#

WORKDIR     /tmp/stonemason/

ADD         . ./

RUN         set -x \
                && pip install -rrequirements-dev.txt \
                && pip install . \
                && apt-get install make \
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
