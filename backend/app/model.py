import onnxruntime
from pathlib import Path
import numpy as np
import os
from PIL import Image


MODEL_NAME = os.getenv("MODEL_NAME")
ort_session = onnxruntime.InferenceSession(str(Path('/models/mmcn') / MODEL_NAME))

def predict(img: Image):
    # crowd counting
    # test if grayscale :
    if (img.mode == 'RGB') or  (img.mode == 'RGBA')  :
        img = img.convert('L')

    if img.size != (1024, 768):
        img = img.resize((1024, 768))

    img = np.asarray(img)
    img = img.reshape((1,1,768,1024)).astype(np.float32)

    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    density_map = ort_outs[0]
    nb_person = np.squeeze(density_map, axis=(0,1)).sum()
    return int(nb_person)
