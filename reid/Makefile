SHELL := /bin/bash

IMAGE ?= kotoracompany/mct-reid
VERSION ?= 0.1.0

echo:
	@echo $(IMAGE):$(VERSION)

build_base:
	docker build -f Dockerfile.base -t $(IMAGE):base .

build:
	docker build -f Dockerfile -t $(IMAGE):$(VERSION) .

start_chroma:
	docker-compose -f tests/chroma-compose.yml up -d

stop_chroma:
	docker-compose -f tests/chroma-compose.yml down

test:
	python3 main.py

start:
	docker-compose up -d

install: build start

stop:
	docker-compose down
