SHELL = /bin/bash

export CURRENT_PATH := $(shell pwd)
export APP = ia-foule
export APP_PORT = 5000

# this is usefull with most python apps in dev mode because if stdout is
# buffered logs do not shows in realtime
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# compose command to merge production file and and dev/tools overrides
export COMPOSE?=docker-compose -f docker-compose.yml

dummy		    := $(shell touch artifacts)
include ./artifacts

models/ssd_mobilenet:
	mkdir -p models/ssd_mobilenet/

models/ssd_mobilenet/frozen_inference_graph.pb: models/ssd_mobilenet
	curl -o ssd_mobilenet.tar.gz http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
	tar xvzf ssd_mobilenet.tar.gz -C models/ssd_mobilenet --strip-components=1
	rm -rf ssd_mobilenet.tar.gz

dev: 
	@echo "Listening on port: $(APP_PORT)"
	@export EXEC_ENV=dev; $(COMPOSE) -f docker-compose-dev.yml up --build

up: models/ssd_mobilenet/frozen_inference_graph.pb
	@echo "Listening on port: $(APP_PORT)"
	@export EXEC_ENV=prod; $(COMPOSE) up -d

test:
	$(COMPOSE) run --rm --name=${APP} backend /bin/sh -c 'pip3 install pytest && pytest tests/'

down:
	@$(COMPOSE) down
