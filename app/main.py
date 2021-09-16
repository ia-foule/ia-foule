import asyncio
from typing import List, Tuple

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import time, sys
from fastapi.logger import logger

import logging

# Get gunicorn logging level
gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static",html = True), name="static")

cascade_classifier = cv2.CascadeClassifier()

class Faces(BaseModel):
    faces: List[Tuple[int, int, int, int]]

camera = cv2.VideoCapture(0)

async def receive(websocket: WebSocket, queue: asyncio.Queue):
    ws_text = await websocket.receive_text()
    if ws_text == "frame":
        logger.debug("Frontend asks for new frame!")
        _, frame = camera.read()
        try:
            queue.put_nowait(frame)
            logger.debug('put bytes in queue')
        except asyncio.QueueFull:
            logger.debug('the queue is full')
            pass


async def detect(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        img = await queue.get()
        logger.debug(f"started at {time.strftime('%X')}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_bytes = cv2.imencode('.jpg', gray)[1].tobytes()
        faces = cascade_classifier.detectMultiScale(gray)
        if len(faces) > 0:
            faces_output = Faces(faces=faces.tolist())
        else:
            faces_output = Faces(faces=[])
        await websocket.send_bytes(gray_bytes)
        #await websocket.send_json(faces_output.dict())
        queue.task_done()

@app.websocket("/face-detection")
async def face_detection(websocket: WebSocket):
    await websocket.accept()
    logger.debug('the websocket is accepted')
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)
    detect_task = asyncio.create_task(detect(websocket, queue))

    try:
        while camera.isOpened():
            await receive(websocket, queue)
    except WebSocketDisconnect:
        detect_task.cancel()
        await websocket.close()


@app.on_event("startup")
async def startup():
    cascade_classifier.load(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
