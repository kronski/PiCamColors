#!/usr/bin/python3

import picamera
import picamera.array
import time
import numpy as np

import signal
import sys

terminated=False
def signal_handler(sig, frame):
    global terminated
    terminated = True

signal.signal(signal.SIGINT, signal_handler)

halfwidth = 0

class MyAnalysis(picamera.array.PiRGBAnalysis):
    def __init__(self, camera):
        super(MyAnalysis, self).__init__(camera)
        self.frame_num = 0

    def analyse(self, a):
        global halfwidth
        lr = int(np.mean(a[:halfwidth,:, 0]))
        lg = int(np.mean(a[:halfwidth,:, 1]))
        lb = int(np.mean(a[:halfwidth,:, 2]))

        rr = int(np.mean(a[halfwidth:,:, 0]))
        rg = int(np.mean(a[halfwidth:,:, 1]))
        rb = int(np.mean(a[halfwidth:,:, 2]))

        lc = (lr << 16) | (lg << 8) | lb

        rc = (rr << 16) | (rg << 8) | rb
        print('C L #%06x R #%06x' % (lc, rc))

        self.frame_num += 1

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    halfwidth = camera.resolution[0]>>1
    camera.framerate = 30

    camera.zoom = (0.36, 0.52, 0.19, 0.19)
    camera.vflip = True
    camera.hflip = True

    length = 5
    totlength = 0

    with MyAnalysis(camera) as output:
        while not terminated:
            camera.start_recording(output, 'rgb')
            camera.wait_recording(length)
            camera.stop_recording()
            totlength += length
        print('FPS: %.2f' % (output.frame_num / totlength))

print("Process done... Closing...")