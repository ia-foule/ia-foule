import asyncio
from typing import List, Tuple
import requests
import io, base64
from PIL import Image, ImageOps
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException, Header
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import matplotlib.pyplot as plt
import time, sys, os

from fastapi.logger import logger as fastapi_logger
import logging

from pathlib import Path

from count import predict


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
def array2url(arr):
    cmap = plt.get_cmap('jet')
    rgba_img = cmap(arr / arr.max(), alpha=(arr != 0) * 1, bytes=True)
    in_mem_file = io.BytesIO()
    img = Image.fromarray(rgba_img, mode='RGBA')
    img.save(in_mem_file, format = "PNG")
    # reset file pointer to start
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()
    url = base64.b64encode(img_bytes).decode('ascii')
    return url

@app.post("/image/")
async def predict_on_image(density: bool = False, file: UploadFile = File(...)):
    if 'image' in file.content_type:
        content = await file.read()
        img = Image.open(io.BytesIO(content))
        img = img.convert('RGB')
        #img.save('/app/tests/data/pexels.jpg')
        nb_person = predict(img)
        if not density:
            nb_person, _ = predict(img)
            return {'nb_person': nb_person}
        else:
            nb_person, density_map = predict(img)
            url = array2url(density_map)
            return {'nb_person': nb_person, 'url':url}
    else:
        raise HTTPException(status_code=422, detail='Not an image')

@app.get("/prediction/")
async def predict_on_url(url: str, density: bool = False, user_agent: Optional[str] = Header(None)):
    try:
        resp = requests.get(url, headers={'User-Agent': user_agent})
        img = Image.open(io.BytesIO(resp.content))

        if not density:
            nb_person, _ = predict(img)
            return {'nb_person': nb_person}
        else:
            nb_person, density_map = predict(img)
            url = array2url(density_map)
            return {'nb_person': nb_person, 'url':url}

            #return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@app.on_event("startup")
async def startup():
    pass
