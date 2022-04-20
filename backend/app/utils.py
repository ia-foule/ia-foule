import matplotlib.pyplot as plt
from PIL import Image
import io, base64

def array2url(arr):
    """ Convert density map array to url base64 encoded,
    understood by html <img src=url>
    """
    cmap = plt.get_cmap('jet')
    rgba_img = cmap(arr / arr.max(), alpha= (arr > arr.std())*1, bytes=True)
    in_mem_file = io.BytesIO()
    img = Image.fromarray(rgba_img, mode='RGBA')
    img.save(in_mem_file, format = "PNG")
    # reset file pointer to start
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()
    url = base64.b64encode(img_bytes).decode('ascii')
    return url
