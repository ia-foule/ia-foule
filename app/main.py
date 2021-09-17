import asyncio
from typing import List, Tuple

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import time, sys, os

from fastapi.logger import logger as fastapi_logger
import logging


app = FastAPI()
app.mount("/static", StaticFiles(directory="static",html = True), name="static")

logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)

cascade_classifier = cv2.CascadeClassifier()

class Faces(BaseModel):
    faces: List[Tuple[int, int, int, int]]

camera = cv2.VideoCapture(0)

async def receive(websocket: WebSocket, queue: asyncio.Queue):
    ws_text = await websocket.receive_text()
    if ws_text == "frame":
        fastapi_logger.info("Frontend asks for new frame!")
        _, frame = camera.read()
        try:
            queue.put_nowait(frame)
            fastapi_logger.info('put bytes in queue')
        except asyncio.QueueFull:
            fastapi_logger.info('the queue is full')
            pass


async def detect(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        img = await queue.get()
        fastapi_logger.info(f"started at {time.strftime('%X')}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_bytes = cv2.imencode('.jpg', gray)[1].tobytes()
        faces = cascade_classifier.detectMultiScale(gray)
        if len(faces) > 0:
            faces_output = Faces(faces=faces.tolist())
        else:
            faces_output = Faces(faces=[])
        #data = {'frame': 'test'}
        #await websocket.send_json(data)
        await websocket.send_bytes(gray_bytes)
        await websocket.send_json(faces_output.dict())
        queue.task_done()

@app.websocket("/face-detection")
async def face_detection(websocket: WebSocket):
    await websocket.accept()
    fastapi_logger.info('the websocket is accepted')
    queue: asyncio.Queue = asyncio.Queue(maxsize=3)
    detect_task = asyncio.create_task(detect(websocket, queue))

    try:
        while camera.isOpened():
            await receive(websocket, queue)
    except WebSocketDisconnect: # Check the connection with the received socket
        detect_task.cancel()
        await websocket.close()
        camera.release()

@app.on_event("startup")
async def startup():
    cascade_classifier.load(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
