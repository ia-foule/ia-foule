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

import onnxruntime
from pathlib import Path

app = FastAPI()
app.mount("/static", StaticFiles(directory="static",html = True), name="static")

logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)

cascade_classifier = cv2.CascadeClassifier()
MODEL_NAME = os.getenv("MODEL_NAME")
ort_session = onnxruntime.InferenceSession(str(Path('/models/mmcn') / MODEL_NAME))


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
        # face detection
        faces = cascade_classifier.detectMultiScale(gray)

        # crowd counting
        ort_inputs = {ort_session.get_inputs()[0].name: cv2.resize(
            gray,(768, 1024)).reshape((1,1,768,1024)).astype(np.float32)}
        ort_outs = ort_session.run(None, ort_inputs)
        density_map = ort_outs[0]
        nb_person = np.squeeze(density_map, axis=(0,1)).sum()
        print(nb_person)
        if len(faces) > 0:
            faces_output = Faces(faces=faces.tolist())
        else:
            faces_output = Faces(faces=[])
        #data = {'frame': 'test'}
        #await websocket.send_json(data)
        faces_output = faces_output.dict()
        faces_output.update(dict(nbPerson=str(nb_person)))
        await websocket.send_bytes(cv2.imencode('.jpg', gray)[1].tobytes())
        await websocket.send_json(faces_output)

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
