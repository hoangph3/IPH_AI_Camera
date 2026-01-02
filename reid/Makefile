SHELL := /bin/bash

IMAGE ?= kotoracompany/mct-reid
VERSION ?= 0.1.3

echo:
	@echo $(IMAGE):$(VERSION)

build_base:
	docker build -f Dockerfile.base -t $(IMAGE):base .

build:
	docker build -f Dockerfile -t $(IMAGE):$(VERSION) .

start_db:
	docker-compose -f tests/db-compose.yml up -d

stop_db:
	docker-compose -f tests/db-compose.yml down

test:
	python3 main.py

start:
	docker-compose up -d

install: build start

stop:
	docker-compose down
