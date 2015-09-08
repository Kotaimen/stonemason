FROM        kotaimen/stonemason-base
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# Install stonemason and run tests
#
WORKDIR     /tmp/stonemason

ADD         . ./

RUN         pip install -rrequirements-dev.txt && \
            pip install . && \
            python setup.py build_ext -if && \
            tox -e py27 && \
            stonemason init && \
            stonemason check && \
            rm -rf /tmp/stonemason

ENTRYPOINT  ["stonemason"]
CMD         ["--help"]

