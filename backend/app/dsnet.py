import onnxruntime
from pathlib import Path
import numpy as np
import os
from PIL import Image

MODEL_NAME = os.getenv("MODEL_NAME")
ort_session = onnxruntime.InferenceSession(str(Path('/models/dsnet') / MODEL_NAME))

mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
mean = np.float64(mean.reshape(1, -1))
stdinv = 1 / np.float64(std.reshape(1, -1))

def predict(img: Image):
    # crowd counting
    # test if grayscale :
    if (img.mode == 'BGR') or  (img.mode == 'RGBA')  :
        img = img.convert('RGB')

    img = np.asarray(img)

    img = (img /255. - mean) * stdinv
    img = img.astype(np.float32)
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0) # batch size
    print(img.shape)
    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    density_map = ort_outs[0]
    density_map = np.squeeze(density_map, axis=(0,1))
    nb_person = density_map.sum()
    return int(nb_person), density_map
