import socket
import time
import imagezmq
import cv2
import zmq
import os

# Patch ImageSender to limit the queue size
# https://github.com/jeffbass/imagezmq/issues/27#issuecomment-931330169
class ImageSenderSmallQueue(imagezmq.ImageSender):
    def init_pubsub(self, address):
        """Creates and inits a socket in PUB/SUB mode
        """

        socketType = zmq.PUB
        self.zmq_context = imagezmq.SerializingContext()
        self.zmq_socket = self.zmq_context.socket(socketType)
        self.zmq_socket.setsockopt(zmq.SNDHWM, 2)
        self.zmq_socket.bind(address)

        # Assign corresponding send methods for PUB/SUB mode
        self.send_image = self.send_image_pubsub
        self.send_jpg   = self.send_jpg_pubsub

# Accept connections on all tcp addresses, port 5555
sender = ImageSenderSmallQueue(connect_to='tcp://*:5555', REQ_REP=False)

rpi_name =  'localhost'#socket.gethostname() # send RPi hostname with each image
print(rpi_name)
time.sleep(2.0)  # allow camera sensor to warm up
cam = cv2.VideoCapture(os.getenv('RTSP_ADDR'))
frame_rate = 1
prev = 0
while True:  # send images until Ctrl-C
    time_elapsed = time.time() - prev
    ret, image = cam.read()
    if time_elapsed > 1./frame_rate and ret:
        print('New frame sent from cam')
        prev = time.time()
        sender.send_image(rpi_name, image)
        # The execution loop will continue even if no subscriber is connected
