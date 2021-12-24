import os
from PIL import Image

MODEL_TYPE_DETECTOR = os.getenv("MODEL_TYPE_DETECTOR").lower()

# Wrapper for the choosen counter model
# TODO: Could be implemented with python class
from faster_rcnn import predict as predict_rcnn
from yolov3 import predict as predict_yolov3

def predict(img: Image, model_type: str =MODEL_TYPE_DETECTOR):
    # detection models
    if MODEL_TYPE_DETECTOR == "yolov3":
        return predict_yolov3(img)
    elif MODEL_TYPE_DETECTOR == "faster-rcnn":
        return predict_rcnn(img)
    else:
        raise Exception('Model %s not implemented yet'%model_type)
