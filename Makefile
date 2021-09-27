SHELL = /bin/bash

export CURRENT_PATH := $(shell pwd)
export APP = ia-foule
# this is usefull with most python apps in dev mode because if stdout is
# buffered logs do not shows in realtime
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
# compose command to merge production file and and dev/tools overrides
export COMPOSE?=docker-compose
export DC_UP_ARGS = #--build --force-recreate

# NETWORK
export DC_NETWORK_OPT = --opt com.docker.network.driver.mtu=1450
export DC_NETWORK = ia-foule
# BACKEND
export BACKEND_PORT=5000
export BACKEND_HOST = backend
# FRONTEND
export FRONTEND_PORT=3000
export FRONTEND_HOST = frontend
# NGINX
export PORT = 80

export MODEL_NAME = mcnn_shtechB_186v7_ri.onnx
dummy		    := $(shell touch artifacts)

DC_UP_ARGS= --force-recreate #s--build

include ./artifacts

#############
#  Network  #
#############
network-stop:
	docker network rm ${DC_NETWORK}

network:
	@docker network create ${DC_NETWORK_OPT} ${DC_NETWORK} 2> /dev/null; true

#############
#  Models   #
#############
models/mmcn:
	mkdir -p models/mmcn/
	wget https://storage.gra.cloud.ovh.net/v1/AUTH_df731a99a3264215b973b3dee70a57af/share/$(MODEL_NAME) -P models/mmcn

backend-dev: #models/mmcn
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start-reload.sh; $(COMPOSE) -f docker-compose.yml -f docker-compose-dev.yml up -d $(DC_UP_ARGS)

backend: models/mmcn
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start.sh; $(COMPOSE) -f docker-compose.yml up -d

test:
	$(COMPOSE) -f docker-compose.yml run --rm --name=${APP} backend /bin/sh -c 'pip3 install pytest && pytest tests/'

exec:
	$(COMPOSE) -f docker-compose.yml exec backend bash

down:
	@$(COMPOSE) -f docker-compose.yml down

##############
#  FRONTEND  #
##############

frontend-dev:
	@echo "Listening on port: $(FRONTEND_PORT)"
	@$(COMPOSE) -f docker-compose-frontend-dev.yml up -d $(DC_UP_ARGS)

frontend-dev-exec:
	@echo "Listening on port: $(FRONTEND_PORT)"
	@$(COMPOSE) -f docker-compose-frontend-dev.yml exec frontend-dev sh


##############
#  NGINX     #
##############

nginx-dev: network
	@$(COMPOSE) -f docker-compose-nginx-dev.yml up -d $(DC_UP_ARGS)
nginx-dev-stop: network
	@$(COMPOSE) -f docker-compose-nginx-dev.yml down
nginx-dev-exec:
	@$(COMPOSE) -f docker-compose-nginx-dev.yml exec nginx-dev bash

##############
#  GENERAL   #
##############

dev: frontend-dev backend-dev nginx-dev
