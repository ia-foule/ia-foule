import ffmpeg
import subprocess
from count import predict
from PIL import Image
import os, io
from pathlib import Path
from utils import array2url

def get_video_size(filename):
    probe = ffmpeg.probe(filename)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    return width, height


def start_ffmpeg_process(in_filename, frame_rate):
    args = (
        ffmpeg
        .input(in_filename)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24', r="%s"%frame_rate)#, vsync="cfr")
        .compile()
    )
    return subprocess.Popen(args, stdout=subprocess.PIPE)


def read_frame(process1, width, height):
    # Note: RGB24 == 3 bytes per pixel.
    frame_size = width * height * 3
    in_bytes = process1.stdout.read(frame_size)
    if len(in_bytes) == 0:
        frame = None
    else:
        assert len(in_bytes) == frame_size
        try:
            frame = Image.frombuffer('RGB', (width, height), in_bytes)
        except ValueError as e:
            print(e)
            frame = None

    return frame

def process_frame(frame):
    '''Count people'''
    nb_person, density_map = predict(frame)
    print('%s persons'%nb_person)
    p = Path('/tmp/nb_person')
    p.write_text("%s"%nb_person)
    # Save density_map in tmpfs volume as url
    p = Path('/tmp/url')
    url = array2url(density_map)
    p.write_text(url)
    return frame

def write_frame(frame):
    p = Path('/tmp/frame.bin')
    img_byte_arr = io.BytesIO()
    frame.save(img_byte_arr, format='jpeg')
    print('save frame')
    p.write_bytes(img_byte_arr.getvalue())

if __name__ == '__main__':
    RTSP_ADDR = os.getenv("RTSP_ADDR")
    print(RTSP_ADDR)
    frame_rate =  os.getenv("FRAME_RATE", 1)
    width, height = get_video_size(RTSP_ADDR)
    process = start_ffmpeg_process(RTSP_ADDR, frame_rate)
    while True:
        in_frame = read_frame(process, width, height)
        if in_frame is not None:
            out_frame = process_frame(in_frame)
            write_frame(out_frame)
            print('new frame')
    process.wait()
