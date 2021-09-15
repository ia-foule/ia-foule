import os
import io
import cv2
import glob
import time
import numpy as np
from functools import reduce
from importlib import import_module
from datetime import datetime, timedelta
from backend.base_camera import BaseCamera


IMAGE_FOLDER = "imgs"

class Camera(BaseCamera):
    # default value
    video_source = 0
    rotation = None
    detector = None
    camera = None

    def __init__(self, camera_config):
        if 'source' in camera_config:
            self.video_source = camera_config['source']
        if 'rotation' in camera_config:
            self.rotation = camera_config['rotation']
        self.frames = self.frames_pc

    def frames_pc(self):
        if self.camera is None or not self.camera.isOpened():
            self.load_camera()
        while True:
            # read current frame
            _, img = self.camera.read()

            if self.rotation:
                if self.rotation == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                if self.rotation == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                if self.rotation == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            yield img

    def release(self):
        self.camera.release()

    def load_detector(self, startID=0):
        MODEL = os.getenv('MODEL')
        Detector = import_module(MODEL).Detector
        self.detector = Detector()

    def load_camera(self):
        self.camera = cv2.VideoCapture(self.video_source)
        if not self.camera.isOpened():
            raise RuntimeError('Could not start camera.')

    def CaptureContinous(self):
        if self.detector is None:
            self.load_detector()
        image = self.get_frame()
        output = self.detector.prediction(image)
        df = self.detector.filter_prediction(output, image)
        if len(df) > 0:
            if (df['class_name']
                    .str
                    .contains('person|bird|cat|wine glass|cup|sandwich')
                    .any()):
                day = datetime.now().strftime("%Y%m%d")
                directory = os.path.join(IMAGE_FOLDER, 'webcam', day)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                image = self.detector.draw_boxes(image, df)
                classes = df['class_name'].unique().tolist()
                hour = datetime.now().strftime("%H%M%S")
                filename_output = os.path.join(
                        directory, "{}_{}_.jpg".format(hour, "-".join(classes))
                        )
                cv2.imwrite(filename_output, image)

    def prediction(self, img, conf_th=0.3, conf_class=[]):
        if self.detector is None:
            self.load_detector()
        output = self.detector.prediction(img)
        df = self.detector.filter_prediction(output, img, conf_th=conf_th, conf_class=conf_class)
        img = self.detector.draw_boxes(img, df)
        return img

    def PeriodicCaptureContinous(self):
        BEAT_INTERVAL = os.getenv('BEAT_INTERVAL')
        interval=BEAT_INTERVAL
        while True:
            self.CaptureContinous()
            time.sleep(interval)

    def generate(self):
        while True: # wait until
            image = self.get_frame()
            if image is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", image)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                    bytearray(encodedImage) + b'\r\n')

if __name__ == '__main__':
    pass
    #camera = Camera()
    #camera.CaptureContinous()
