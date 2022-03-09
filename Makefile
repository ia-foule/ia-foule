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
export BACKEND_HOST=backend
export LOG_LEVEL=trace # in dev mode only
export FRAME_RATE=1 # Frame rate for rtsp client

# FRONTEND
export FRONTEND_PORT=3000
export FRONTEND_HOST = frontend
# NGINX
export PORT = 80

# RTSP SERVER FOR TESTING
export RTSP_PORT=8554
export RTSP_ADDR=rtsp://vlc-server:8554/test.sdp

# DATA AND MODELS
export OVH_BUCKET = https://storage.gra.cloud.ovh.net/v1/AUTH_df731a99a3264215b973b3dee70a57af/share
export MODEL_NAME_MOBILECOUNT = mobilecount_shtechBv11_da_ri.onnx
export MODEL_NAME_DSNET = dsnet_shtechBv11_da_ri.onnx
export MODEL_NAME_MMCN = mcnn_shtechB_194v11_da_ri.onnx
export MODEL_NAME_DETECTOR = faster_rcnn_r50_fpn_1x_coco_20200130-047c8118_s.onnx

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

models/mmcn:
	mkdir -p models/mmcn/
	wget $(OVH_BUCKET)/$(MODEL_NAME_MMCN) -P models/mmcn
models/dsnet:
	mkdir -p models/dsnet/
	wget $(OVH_BUCKET)/$(MODEL_NAME_DSNET) -P models/dsnet
models/mobilecount:
		mkdir -p models/mobilecount/
		wget $(OVH_BUCKET)/$(MODEL_NAME_MOBILECOUNT) -P models/mobilecount
models/detector:
		mkdir -p models/dsnet/
		wget $(OVH_BUCKET)/$(MODEL_NAME_DETECTOR) -P models/faster_rcnn
models/yolov3:
		mkdir -p models/yolov3/
		wget https://github.com/onnx/models/raw/master/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx -P models/yolov3

make download-models:  models/mmcn models/dsnet models/mobilecount models/detector


#############
#  Backend  #
#############

backend-dev: network
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start-reload.sh; $(COMPOSE) -f docker-compose.yml -f docker-compose-dev.yml up -d $(DC_UP_ARGS)

backend:
	@echo "Listening on port: $(BACKEND_PORT)"
	@export COMMAND_PARAMS=/start.sh; $(COMPOSE) -f docker-compose.yml up -d

test:
	$(COMPOSE) -f docker-compose.yml -f docker-compose-dev.yml  run  --rm --name=${APP} backend /bin/sh -c 'pip3 install pytest && pytest tests/ -s'

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
nginx-down:
	@$(COMPOSE) -f docker-compose-nginx-dev.yml down


##############
# VLC-SERVER #
##############
vlc-server-build:
	@$(COMPOSE) -f docker-compose-vlc-server.yml build
vlc-server-up:
	@$(COMPOSE) -f docker-compose-vlc-server.yml up -d $(DC_UP_ARGS)
vlc-server-logs:
	@$(COMPOSE) logs vlc-server
vlc-server-down:
	@$(COMPOSE) -f docker-compose-vlc-server.yml down

##############
#  GENERAL   #
##############

dev: frontend-dev backend-dev nginx-dev
down: frontend-down backend-down nginx-down
