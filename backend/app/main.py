import asyncio
from typing import List, Tuple
import requests
import io
from PIL import Image, ImageOps
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Header
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import time, sys, os, json

from fastapi.logger import logger as fastapi_logger
import logging

from pathlib import Path

from count import predict as predict_count
from detect import predict as predict_detect
from fusion import predict as predict_fusion

from utils import array2url

app = FastAPI()

logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)

################
# from server  #
################

async def receive(websocket: WebSocket):
    # Just a ping-pong to check the connection
    ws_text = await websocket.receive_text()

async def detect(websocket: WebSocket, density=False, detection=False):
    # Detection is already made by client_ffmpeg, get binary frame and send through
    # websocket to the brower.
    p = Path('/tmp/frame.bin')
    st_mtime_ns_read = 0
    while True:
        await asyncio.sleep(0.1)
        st_mtime_ns = p.stat().st_mtime_ns
        #print(st_mtime_ns)
        if st_mtime_ns > st_mtime_ns_read:
            st_mtime_ns_read = st_mtime_ns
            await websocket.send_bytes(p.read_bytes())
            await asyncio.sleep(0.2) # wait for ffmpeg process to write
            with Path('/tmp/result.json').open() as fp:
                result = json.load(fp)
            await websocket.send_json(result)

@app.websocket("/video-server")
async def face_detection(websocket: WebSocket, density: bool = False, detection: bool = False):
    await websocket.accept()
    #await  websocket.send_json(json.dumps({'nb_person': 0}))
    detect_task = asyncio.create_task(detect(websocket, density, detection))
    try:
        while True:
            await receive(websocket)
    except WebSocketDisconnect: # Check the connection with the received socket
        print('WS disco')
        detect_task.cancel()
        await websocket.close()

################
# from browser #
################

async def receive_for_browser(websocket: WebSocket, queue: asyncio.Queue):
    bytes = await websocket.receive_bytes()
    try:
        queue.put_nowait(bytes)
    except asyncio.QueueFull:
        pass

async def detect_for_browser(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        bytes = await queue.get()
        img = Image.open(io.BytesIO(bytes))
        nb_person = predict_count(img)
        await websocket.send_text(str(nb_person))
        queue.task_done()

@app.websocket("/video-browser")
async def video_browser(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=10)
    detect_task = asyncio.create_task(detect_for_browser(websocket, queue))
    try:
        while True:
            await receive_for_browser(websocket, queue)
    except WebSocketDisconnect:
        print("WS disco")
        detect_task.cancel()
        await websocket.close()

################
# Other routes #
################


@app.post("/image/")
async def predict_on_image(density: bool = False,
                            detection: bool = False,
                            fusion: bool =False,  # Run both and fuse their result
                            file: UploadFile = File(...)):
    if 'image' in file.content_type:
        content = await file.read()
        img = Image.open(io.BytesIO(content))
        img = img.convert('RGB')
        if fusion:
            nb_person, density_map, bboxes = predict_fusion(img)
            result = {
                    'nb_person' : nb_person,
                    'nb_person_counted': int(density_map.sum()),
                    'url': array2url(density_map),
                    'bboxes':bboxes,
                    'width': img.size[0],
                    'height': img.size[1]
                    }
            return result
        # Prepare result
        result = {}
        if not density:
            nb_person, _ = predict_count(img)
            result.update({'nb_person': nb_person})
        else:
            nb_person, density_map = predict_count(img)
            url = array2url(density_map)
            result.update({'nb_person': nb_person, 'url': url})
        if detection:
            bboxes = predict_detect(img)
            result.update({'bboxes':bboxes, 'width': img.size[0], 'height': img.size[1]})
        return result

    else:
        raise HTTPException(status_code=422, detail='Not an image')

@app.get("/prediction/")
async def predict_on_url(url: str,
                        density: bool = False,  # Compute density map
                        detection: bool = False, # Run detection model
                        fusion: bool =False,  # Run both and fuse their result
                        user_agent: Optional[str] = Header(None)):
    try:
        resp = requests.get(url, headers={'User-Agent': user_agent})
        img = Image.open(io.BytesIO(resp.content))
        if fusion:
            nb_person, density_map, bboxes = predict_fusion(img)
            result = {
                    'nb_person' : nb_person,
                    'nb_person_counted': int(density_map.sum()),
                    'url': array2url(density_map),
                    'bboxes':bboxes,
                    'width': img.size[0],
                    'height': img.size[1]
                    }
            return result
        # Prepare result
        result = {}
        if not density:
            nb_person, _ = predict_count(img)
            result.update({'nb_person': nb_person})
        else:
            nb_person, density_map = predict_count(img)
            url = array2url(density_map)
            result.update({'nb_person': nb_person, 'url': url})
        if detection:
            bboxes = predict_detect(img)
            result.update({'bboxes':bboxes, 'width': img.size[0], 'height': img.size[1]})
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@app.on_event("startup")
async def startup():
    pass
