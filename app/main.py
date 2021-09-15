import asyncio
from typing import List, Tuple

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import time
app = FastAPI()
app.mount("/static", StaticFiles(directory="static",html = True), name="static")
cascade_classifier = cv2.CascadeClassifier()

class Faces(BaseModel):
    faces: List[Tuple[int, int, int, int]]


async def receive(websocket: WebSocket, queue: asyncio.Queue):
    bytes = await websocket.receive_bytes()
    try:
        queue.put_nowait(bytes)
        print('put bytes in queue')
    except asyncio.QueueFull:
        #print('the queue is full')
        pass


async def detect(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        bytes = await queue.get()
        print(f"started at {time.strftime('%X')}")
        data = np.frombuffer(bytes, dtype=np.uint8)
        img = cv2.imdecode(data, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade_classifier.detectMultiScale(gray)
        print("process bytes")
        await asyncio.sleep(5)
        if len(faces) > 0:
            faces_output = Faces(faces=faces.tolist())
        else:
            faces_output = Faces(faces=[])
        await websocket.send_json(faces_output.dict())
        queue.task_done()
        print('task done')

@app.websocket("/face-detection")
async def face_detection(websocket: WebSocket):
    await websocket.accept()
    print('the websocket is accepted')
    queue: asyncio.Queue = asyncio.Queue(maxsize=10)
    detect_task = asyncio.create_task(detect(websocket, queue))
    try:
        while True:
            await receive(websocket, queue)
    except WebSocketDisconnect:
        detect_task.cancel()
        await websocket.close()


@app.on_event("startup")
async def startup():
    cascade_classifier.load(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
