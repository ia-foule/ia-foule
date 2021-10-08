from model import predict
from PIL import Image, ImageOps
from pathlib import Path

def test_predict():
    img_path = Path(__file__).resolve().parent / 'data/IMG_1.jpg'
    img = Image.open(img_path)
    nb_person = predict(img)
    assert nb_person == 37
