FROM        kotaimen/stonemason-base:0.2.0
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# Install stonemason and run tests
#

WORKDIR     /tmp/stonemason/

ADD         . ./

RUN         pip install -rrequirements-dev.txt && \
            pip install . && \
            python setup.py build_ext -if && \
            tox -e py27 && \
            rm -rf /tmp/stonemason

#
# Create a sample at /var/lib/stonemason/map_gallery
#
WORKDIR     /var/lib/stonemason/

RUN         stonemason init && \
            stonemason check

#
# Entry
#
EXPOSE      80
ENTRYPOINT  ["stonemason"]
CMD         [tileserver", "--bind=0.0.0.0:80"]
