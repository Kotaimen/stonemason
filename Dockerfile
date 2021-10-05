FROM 889515947644.dkr.ecr.us-west-2.amazonaws.com/mapnik:bionic

# Install stonemason
WORKDIR /tmp/workdir
ADD . ./
RUN set -eux; \
        pip3 install . ; \
        rm -rf *;


# Create a sample at /var/lib/stonemason/map_gallery
WORKDIR /var/lib/stonemason/
RUN set -eux; \
  stonemason init
RUN  stonemason check


# Entry
EXPOSE 80
ENTRYPOINT ["stonemason"]
CMD ["tileserver", "--bind=0.0.0.0:80"]
