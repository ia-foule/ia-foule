from mobilecount import predict
from PIL import Image, ImageOps
from pathlib import Path
import time
def test_predict():
    img_path = Path(__file__).resolve().parent / 'data/IMG_1.jpg'
    img = Image.open(img_path)
    t1 = time.time()
    nb_person, _ = predict(img)
    exec_time = time.time() - t1
    print("execution time: %s"%exec_time)
    assert nb_person == 21
    assert exec_time < 1, 'take more than 4 seconds! '
