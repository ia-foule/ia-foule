import asyncio
from typing import List, Tuple
import requests
import io
from PIL import Image, ImageOps
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from pydantic import BaseModel
import time, sys, os

from fastapi.logger import logger as fastapi_logger
import logging


from model import predict

app = FastAPI()

logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)


class Faces(BaseModel):
    faces: List[Tuple[int, int, int, int]]



################
# from server  #
################


async def fill(camera, queue: asyncio.Queue):
    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            #print('video is finished!')
            break
        try:
            queue.put_nowait(frame)
            #print('put frame in queue')
            fastapi_logger.info('put frame in queue')
        except asyncio.QueueFull:
            fastapi_logger.info('the queue is full of frame')
            pass

async def receive(websocket: WebSocket, queue: asyncio.Queue, queue_frame: asyncio.LifoQueue):
    ws_text = await websocket.receive_text()
    if (ws_text == "frame") and (not queue.full()):
        #print("Frontend asks for new frame!")
        fastapi_logger.info("Frontend asks for new frame!")
        frame = await queue_frame.get()
        queue.put_nowait(frame)
        fastapi_logger.info('put bytes in queue')
        queue_frame.task_done()

async def detect(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        img = await queue.get()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        fastapi_logger.info(f"started at {time.strftime('%X')}")
        nb_person = predict(img)

        await websocket.send_text(str(nb_person))

        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format="jpeg")
        await websocket.send_bytes(imgByteArr.getvalue())

        queue.task_done()

@app.websocket("/video-server")
async def face_detection(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("0")
    camera = cv2.VideoCapture("/app/tests/data/Pexels Videos 1625972.mp4")
    queue_frame: asyncio.LifoQueue = asyncio.Queue(maxsize=5)
    fill_task = asyncio.create_task(fill(camera, queue_frame))
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)
    detect_task = asyncio.create_task(detect(websocket, queue))

    try:
        while True:
            await receive(websocket, queue, queue_frame)

    except WebSocketDisconnect: # Check the connection with the received socket
        print('WS disco')
        detect_task.cancel()
        fill_task.cancel()
        await websocket.close()
        camera.release()

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
async def predict_on_url(url: str):
    try:
        resp = requests.get(url)
        img = Image.open(io.BytesIO(resp.content))
        nb_person = predict(img)
        return {'nb_person': nb_person}
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@app.on_event("startup")
async def startup():
    pass
