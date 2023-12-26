SHELL := /bin/bash

IMAGE ?= kotoracompany/mct-tracking
VERSION ?= 0.1.0

echo:
	@echo $(IMAGE):$(VERSION)

build_base:
	docker build -f Dockerfile.base -t $(IMAGE):base .

build:
	docker build -f Dockerfile -t $(IMAGE):$(VERSION) .

test:
	python3 main.py

start:
	docker-compose up -d

install: build start

stop:
	docker-compose down
