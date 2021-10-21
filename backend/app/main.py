import asyncio
from typing import List, Tuple
import requests
import io
from PIL import Image, ImageOps
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

import time, sys, os

from fastapi.logger import logger as fastapi_logger
import logging

from pathlib import Path

from model import predict


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

async def detect(websocket: WebSocket):
    # Detection is already made by client_ffmpeg, get binary frame and send through
    # websocket to the brower.
    p = Path('/tmp/frame.bin')
    st_mtime_ns_read = 0
    while True:
        st_mtime_ns = p.stat().st_mtime_ns
        if st_mtime_ns > st_mtime_ns_read:
            st_mtime_ns_read = p.stat().st_mtime_ns
            await websocket.send_bytes(p.read_bytes())
            await websocket.send_text(Path('/tmp/count').read_text())
@app.websocket("/video-server")
async def face_detection(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("0")
    detect_task = asyncio.create_task(detect(websocket))
    try:
        while True:
            await receive(websocket)
    except WebSocketDisconnect: # Check the connection with the received socket
        print('WS disco')
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
        nb_person = predict(img)
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
async def predict_on_image(file: UploadFile = File(...)):
    if 'image' in file.content_type:
        content = await file.read()
        img = Image.open(io.BytesIO(content))
        img = img.convert('RGB')
        #img.save('/app/tests/data/pexels.jpg')
        nb_person = predict(img)
        return {'nb_person': nb_person}
    else:
        raise HTTPException(status_code=422, detail='Not an image')

@app.get("/prediction/")
async def predict_on_url(url: str, user_agent: Optional[str] = Header(None)):
    try:
        resp = requests.get(url, headers={'User-Agent': user_agent})
        img = Image.open(io.BytesIO(resp.content))
        nb_person = predict(img)
        return {'nb_person': nb_person}
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@app.on_event("startup")
async def startup():
    pass
