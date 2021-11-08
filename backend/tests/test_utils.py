from utils import array2url
import numpy as np
import time

def test_array2url():
    arr = np.ones((300,600))
    arr = np.expand_dims(arr, axis=0) # channel size
    t1 = time.time()
    url = array2url(arr)
    exec_time = time.time() - t1
    print("execution time: %s"%exec_time)
    assert url == """iVBORw0KGgoAAAANSUhEUgAAASwAAAABCAYAAABkOJMpAAAAF0lEQVR4nGOsZ2D4zzAKRsEoGAVDAAAABW4BgMXIuRkAAAAASUVORK5CYII="""
