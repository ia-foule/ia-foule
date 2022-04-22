import onnxruntime
from pathlib import Path
import numpy as np
import os
from PIL import Image

MODEL_NAME = os.getenv("MODEL_NAME_MOBILECOUNT")
ort_session = onnxruntime.InferenceSession(str(Path('/models/mobilecount') / MODEL_NAME))

#mean = np.array([0.452016860247, 0.447249650955, 0.431981861591])
#std = np.array([0.23242045939, 0.224925786257, 0.221840232611])
mean = np.array([0.48879814, 0.4907805, 0.4841541])
std = np.array([0.22630496, 0.22669446, 0.22931112])

mean = np.float64(mean.reshape(1, -1))
stdinv = 1 / np.float64(std.reshape(1, -1))

def predict(img: Image):
    # crowd counting
    # test if grayscale :
    if (img.mode == 'BGR') or  (img.mode == 'RGBA')  :
        img = img.convert('RGB')

    img = np.asarray(img)
    img = (img / 255. - mean) * stdinv
    img = img.astype(np.float32)
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis=0) # batch size

    ort_inputs = {ort_session.get_inputs()[0].name: img}
    ort_outs = ort_session.run(None, ort_inputs)
    density_map = ort_outs[0]
    density_map = np.squeeze(density_map, axis=(0,1))
    nb_person = density_map.sum()

    return int(nb_person), density_map
