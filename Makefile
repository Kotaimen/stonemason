.PHONY: build

CUR_DIR = $(CURDIR)

build:
	docker build -t mapnik:bionic docker-mapnik
	docker build -t stonemason:0.3.3-dev .
