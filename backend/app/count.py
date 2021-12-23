import os
from PIL import Image

MODEL_TYPE = os.getenv("MODEL_TYPE").lower()

# Wrapper for the choosen counter model
# TODO: Could be implemented with python class
from mmcn import predict as predict_mmcn
from dsnet import predict as predict_dsnet
from mobilecount import predict as predict_mobilecount

def predict(img: Image, model_type: str =MODEL_TYPE):
    # crowd counting
    if MODEL_TYPE == "mmcn":
        return predict_mmcn(img)
    elif MODEL_TYPE == "dsnet":
        return predict_dsnet(img)
    elif MODEL_TYPE == "mobilecount":
        return predict_mobilecount(img)
    else:
        raise Exception('Model %s not implemented yet'%model_type)
