import cv2
from backend.ssd_detection import Detector as Detector_SSD

def test_ssd():
    image = cv2.imread("./imgs/image.jpeg")

    detector = Detector_SSD()
    output = detector.prediction(image)
    df = detector.filter_prediction(output, image)
    image = detector.draw_boxes(image, df)
    print(df)
    assert df.shape[0] > 1
    assert any(df['class_name'].str.contains('person'))
    cv2.imwrite("./imgs/outputcv.jpg", image)
