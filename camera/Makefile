SHELL := /bin/bash

IMAGE ?= kotoracompany/mct-camera
VERSION ?= 0.1.0

echo:
	@echo $(IMAGE):$(VERSION)

build_base:
	docker build -f Dockerfile.base -t $(IMAGE):base .

build:
	docker build -f Dockerfile -t $(IMAGE):$(VERSION) .

start_redis:
	docker run -dp 6379:6379 --name mct_redis redis:7.0.4

stop_redis:
	docker rm -f mct_redis

test:
	python3 main.py

start:
	docker-compose up -d

install: build start

stop:
	docker-compose down
