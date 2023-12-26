SHELL := /bin/bash

IMAGE ?= kotoracompany/mct-tracking
VERSION ?= 0.1.0

echo:
	@echo $(IMAGE):$(VERSION)

build_base:
	docker build -f Dockerfile.base -t $(IMAGE):base .

build:
	docker build -f Dockerfile -t $(IMAGE):$(VERSION) .

start_mongo:
	docker compose -f tests/mongo-compose.yml up -d

stop_mongo:
	docker compose -f tests/mongo-compose.yml down

test:
	python3 main.py

start:
	docker compose up -d

install: build start

stop:
	docker-compose down
