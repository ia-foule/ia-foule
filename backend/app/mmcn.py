import onnxruntime
from pathlib import Path
import numpy as np
import os
from PIL import Image

MODEL_NAME = os.getenv("MODEL_NAME_MMCN")
ort_session = onnxruntime.InferenceSession(str(Path('/models/mmcn') / MODEL_NAME))

def predict(img: Image):
    # crowd counting
    # test if grayscale :
    if (img.mode == 'RGB') or  (img.mode == 'RGBA')  :
        img = img.convert('L')

    img = np.asarray(img).astype(np.float32)
    img = np.expand_dims(img, axis=(0, 1)) # batch size

    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    density_map = ort_outs[0]
    density_map = np.squeeze(density_map, axis=(0,1))
    nb_person = density_map.sum()

    return int(nb_person), density_map
