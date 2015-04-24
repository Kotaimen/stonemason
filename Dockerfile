FROM        kotaimen/stonemason-base:0.2.0.dev0
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
            tox -e py27geo && \
            stonemason init && \
            stonemason check && \
            rm -rf $WORKDIR

ENTRYPOINT  stonemason
CMD         --help
