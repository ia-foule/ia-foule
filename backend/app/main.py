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

cascade_classifier = cv2.CascadeClassifier()

class Faces(BaseModel):
    faces: List[Tuple[int, int, int, int]]

camera = cv2.VideoCapture("/imgs/Pexels Videos 2740.mp4")

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
    bytes = await websocket.receive_bytes()

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
        img.save('/app/tests/data/pexels.jpg')
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
    cascade_classifier.load(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
