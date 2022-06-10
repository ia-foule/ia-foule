SHELL = /bin/bash

export CURRENT_PATH := $(shell pwd)
export APP = ia-foule
export APP_VERSION := 1.2
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
export BACKEND_HOST=backend
export LOG_LEVEL=trace # in dev mode only
export FRAME_RATE=1 # Frame rate for rtsp client

# FRONTEND
export FRONTEND_PORT=3000
export FRONTEND_HOST = frontend
# NGINX
export PORT = 80

# RTSP SERVER FOR TESTING
export RTSP_PORT=8854
export RTSP_ADDR=rtsp://vlc-server:8554/test.sdp
export VLC_DATA_PATH=${CURRENT_PATH}/backend/tests/data

# BUILD OPTIONS
export BUILD_DIR = ${CURRENT_PATH}/${APP}-build
export FILE_FRONTEND_DIST_APP_VERSION = $(APP)-$(APP_VERSION)-frontend-dist.tar.gz

# DATA AND MODELS
export OVH_BUCKET = https://storage.gra.cloud.ovh.net/v1/AUTH_df731a99a3264215b973b3dee70a57af/share
export MODEL_NAME_MOBILECOUNT = mobilecount_shtechBv11_da_ri.onnx
export MODEL_NAME_DSNET = dsnet_shtechBv11_da_ri.onnx
export MODEL_NAME_MMCN = mcnn_shtechB_194v11_da_ri.onnx
export MODEL_NAME_DETECTOR = faster_rcnn_r50_fpn_1x_coco_20200130-047c8118_s.onnx
export MODEL_PATH=${CURRENT_PATH}/models

# CHOOSE THE MODELS TO USE
export MODEL_TYPE = mobilecount
export MODEL_TYPE_DETECTOR = yolov3

dummy		  := $(shell touch artifacts)

DC_UP_ARGS = --force-recreate #s--build

# REMAPPING SOME VARIABLES
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

$(MODEL_PATH)/mmcn:
	mkdir -p $(MODEL_PATH)/mmcn/
	wget $(OVH_BUCKET)/models/$(MODEL_NAME_MMCN) -P $(MODEL_PATH)/mmcn
$(MODEL_PATH)/dsnet:
	mkdir -p $(MODEL_PATH)/dsnet/
	wget $(OVH_BUCKET)/models/$(MODEL_NAME_DSNET) -P $(MODEL_PATH)/dsnet
$(MODEL_PATH)/mobilecount:
		mkdir -p $(MODEL_PATH)/mobilecount/
		wget $(OVH_BUCKET)/models/$(MODEL_NAME_MOBILECOUNT) -P $(MODEL_PATH)/mobilecount
$(MODEL_PATH)/faster_rcnn:
		mkdir -p $(MODEL_PATH)/faster_rcnn/
		wget $(OVH_BUCKET)/models/$(MODEL_NAME_DETECTOR) -P $(MODEL_PATH)/faster_rcnn
$(MODEL_PATH)/yolov3:
		mkdir -p $(MODEL_PATH)/yolov3/
		wget $(OVH_BUCKET)/models/yolov3-10.onnx -P $(MODEL_PATH)/yolov3

make download-models: $(MODEL_PATH)/mmcn $(MODEL_PATH)/dsnet $(MODEL_PATH)/mobilecount $(MODEL_PATH)/faster_rcnn $(MODEL_PATH)/yolov3

#############
#  Backend  #
#############

backend-build:
	@$(COMPOSE) -f  docker-compose.yml build $(DC_BUILD_ARGS)

backend-dev: network
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start-reload.sh; $(COMPOSE) -f docker-compose.yml -f docker-compose-dev.yml up -d $(DC_UP_ARGS)

backend-prod:
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start.sh; $(COMPOSE) -f docker-compose.yml up -d $(DC_UP_ARGS)

test:
	$(COMPOSE) -f docker-compose.yml -f docker-compose-dev.yml run --rm --name=${APP} backend /bin/sh -c 'pip3 install pytest && pytest tests/ -s'

test-rstp: up-vlc-server
	@echo "Vlc rtsp server is running : open rtsp://localhost:$(RTSP_PORT)/test.sdp"
	@echo "Test the iafoule app by choosing Rtsp"

backend-exec:
	$(COMPOSE) -f docker-compose.yml exec backend bash

backend-down:
	@$(COMPOSE) -f docker-compose.yml down

##############
#  FRONTEND  #
##############

frontend-dev-build:
	@echo "Build frontend"
	@$(COMPOSE) -f docker-compose-frontend-dev.yml build $(DC_BUILD_ARGS)

frontend-dev:
	@echo "Listening on port: $(FRONTEND_PORT)"
	@$(COMPOSE) -f docker-compose-frontend-dev.yml up -d $(DC_UP_ARGS)

frontend-dev-exec:
	@echo "Listening on port: $(FRONTEND_PORT)"
	@$(COMPOSE) -f docker-compose-frontend-dev.yml exec frontend-dev sh

frontend-down:
	@$(COMPOSE) -f docker-compose-frontend-dev.yml down


##############
#  NGINX     #
##############

nginx-dev: network
	@$(COMPOSE) -f docker-compose-nginx-dev.yml up -d $(DC_UP_ARGS)
nginx-dev-stop: network
	@$(COMPOSE) -f docker-compose-nginx-dev.yml down
nginx-dev-exec:
	@$(COMPOSE) -f docker-compose-nginx-dev.yml exec nginx-dev bash
nginx-dev-down:
	@$(COMPOSE) -f docker-compose-nginx-dev.yml down
nginx-prod: network
	@$(COMPOSE) -f docker-compose-nginx.yml up -d $(DC_UP_ARGS)
nginx-down:
	@$(COMPOSE) -f docker-compose-nginx.yml down
nginx-dev-exec:
	@$(COMPOSE) -f docker-compose-nginx.yml exec nginx bash
##############
# VLC-SERVER #
##############
$(VLC_DATA_PATH)/5.mp4:
	wget $(OVH_BUCKET)/videos/5.mp4 -P $(VLC_DATA_PATH)

vlc-server-build:
	@$(COMPOSE) -f docker-compose-vlc-server.yml build
vlc-server-up: $(VLC_DATA_PATH)/5.mp4
	@$(COMPOSE) -f docker-compose-vlc-server.yml up -d $(DC_UP_ARGS)
vlc-server-logs:
	@$(COMPOSE) logs vlc-server
vlc-server-down:
	@$(COMPOSE) -f docker-compose-vlc-server.yml down

###############
# BUILD STAGE #
###############
build: frontend-build nginx-build backend-build

frontend-build: network frontend-build-dist $(BUILD_DIR)/$(FILE_FRONTEND_DIST_APP_VERSION)

nginx-build:
	@echo building ${APP} nginx
	cp $(BUILD_DIR)/$(FILE_FRONTEND_DIST_APP_VERSION) nginx/
	@$(COMPOSE) -f docker-compose-nginx.yml build $(DC_BUILD_ARGS)

frontend-build-dist:
	@echo building ${APP} frontend in ${FRONTEND}
	@$(COMPOSE) -f docker-compose-frontend-build.yml build $(DC_BUILD_ARGS)


build-dir:
	@if [ ! -d "$(BUILD_DIR)" ] ; then mkdir -p $(BUILD_DIR) ; fi

$(BUILD_DIR)/$(FILE_FRONTEND_DIST_APP_VERSION): build-dir
	@$(COMPOSE) -f docker-compose-frontend-build.yml run -T frontend-build sh -c "npm run build > /dev/null 2>&1 && tar czf - public -C /app" > $(BUILD_DIR)/$(FILE_FRONTEND_DIST_APP_VERSION)

##############
#  GENERAL   #
##############

dev: frontend-dev backend-dev nginx-dev
down: frontend-down backend-down nginx-dev-down

up: backend-prod nginx-prod
stop: backend-down nginx-down
