import onnxruntime
from pathlib import Path
import numpy as np
import os
from PIL import Image

ort_session = onnxruntime.InferenceSession(str(Path('/models/yolov3/yolov3-10.onnx')), None)

# The class to keep is the 0

# this function is from yolo3.utils.letterbox_image
def letterbox_image(image, size):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128,128,128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))
    return new_image

def preprocess(img):
    model_image_size = (416, 416)
    boxed_image = letterbox_image(img, tuple(reversed(model_image_size)))
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.transpose(image_data, [2, 0, 1])
    image_data = np.expand_dims(image_data, 0)
    return image_data

def postprocess(boxes, scores, indices):
    out_boxes, out_scores, out_classes = [], [], []
    for idx_ in indices:
        #import pdb; pdb.set_trace()
        out_classes.append(idx_[1])
        out_scores.append(scores[tuple(idx_)])
        idx_1 = (idx_[0], idx_[2])
        out_boxes.append(boxes[idx_1])
    return out_boxes, out_scores, out_classes

def det_bboxes(boxes,
              scores,
              indices,
              class_names=None,
              score_thr=0,
              ):
    """Save bboxes and class labels (with scores) on an image.
    Args:
        bboxes (ndarray): Bounding boxes, shaped (n, 4)
        scores (ndarray): Score of bboxes, shaped (n, 1)
        indices (ndarray): Indice of bboxes, shaped (n, 1)
        class_names (list[str]): Names of each classes.
        score_thr (float): Minimum score of bboxes to be shown.
    """
    to_save = []

    for box, score, indice in zip(boxes, scores, indices):
        if score > score_thr and indice == 0:
            to_save.append({'x1': int(box[1]),'y1': int(box[0]),
                            'x2': int(box[3]),'y2': int(box[2]),
                            'class_name':'person','confidence':float(score)})
    return to_save


def predict(img: Image):
    # crowd counting
    # test if grayscale :
    if (img.mode == 'BGR') or (img.mode == 'RGBA')  :
        img = img.convert('RGB')

    # input
    image_size = np.array([img.size[1], img.size[0]], dtype=np.float32).reshape(1, 2)

    img = preprocess(img)

    ort_inputs = {ort_session.get_inputs()[0].name: img,
                ort_session.get_inputs()[1].name: image_size}
    ort_outs = ort_session.run(None, ort_inputs)
    out_boxes, out_scores, out_classes = postprocess(*ort_outs)
    result = det_bboxes(out_boxes, out_scores, out_classes)

    return result
