FROM        kotaimen/stonemason-base
MAINTAINER  Kotaimen <kotaimen.c@gmail.com>
ENV         DEBIAN_FRONTEND noninteractive

#
# Set locale, otherwise Click complains, see http://click.pocoo.org/3/python3/
#
RUN         locale-gen en_US.UTF-8
ENV         LANG en_US.UTF-8
ENV         LANGUAGE en_US:en
ENV         LC_ALL en_US.UTF-8

#
# Install stonemason and run tests
#
WORKDIR     /tmp/stonemason

ADD         . ./

RUN         pip install -rrequirements-dev.txt && \
            pip install . && \
            python setup.py build_ext -if && \
            stonemason init && \
            stonemason check && \
            rm -rf /tmp/stonemason

ENTRYPOINT  ["stonemason"]
CMD         ["--help"]

