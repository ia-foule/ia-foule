SHELL = /bin/bash

export CURRENT_PATH := $(shell pwd)
export APP = ia-foule
export APP_PORT = 5000

# this is usefull with most python apps in dev mode because if stdout is
# buffered logs do not shows in realtime
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export DC_NETWORK=ia-foule
# compose command to merge production file and and dev/tools overrides
export COMPOSE?=docker-compose -f docker-compose.yml

dummy		    := $(shell touch artifacts)
include ./artifacts

#############
#  Network  #
#############

network-stop:
	docker network rm ${DC_NETWORK}

network:
	@docker network create ${DC_NETWORK} 2> /dev/null; true

models/mmcn:
	mkdir -p models/mmcn/
	wget https://storage.gra.cloud.ovh.net/v1/AUTH_df731a99a3264215b973b3dee70a57af/share/mcnn_shtechB_186v7_ri.onnx

dev: models/mmcn
	@echo "Listening on port: $(APP_PORT)"
	@export COMMAND_PARAMS=/start-reload.sh; $(COMPOSE) -f docker-compose-dev.yml up #--build

up: models/mmcn
	@echo "Listening on port: $(APP_PORT)"
	@export COMMAND_PARAMS=/start.sh; $(COMPOSE) up -d

test:
	$(COMPOSE) run --rm --name=${APP} backend /bin/sh -c 'pip3 install pytest && pytest tests/'

exec:
	$(COMPOSE) exec  backend bash

down:
	@$(COMPOSE) down
