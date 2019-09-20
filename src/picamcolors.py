#!/usr/bin/python3

import picamera
import picamera.array
import time
import numpy as np
import signal
import sys
import errno

terminated=False
def signal_handler(sig, frame):
    stop()

def sigpipe_handler(sig,frame):
    stop()
    
def stop():
    global terminated
    if camera.recording:
        camera.stop_recording()
    terminated = True

signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGPIPE, sigpipe_handler)

halfwidth = 0

class MyAnalysis(picamera.array.PiRGBAnalysis):
    def __init__(self, camera):
        super(MyAnalysis, self).__init__(camera)
        self.frame_num = 0

    def analyse(self, a):
        lr = int(np.mean(a[:halfwidth,:, 0]))
        lg = int(np.mean(a[:halfwidth,:, 1]))
        lb = int(np.mean(a[:halfwidth,:, 2]))

        rr = int(np.mean(a[halfwidth:,:, 0]))
        rg = int(np.mean(a[halfwidth:,:, 1]))
        rb = int(np.mean(a[halfwidth:,:, 2]))

        lc = (lr << 16) | (lg << 8) | lb
        rc = (rr << 16) | (rg << 8) | rb

        print('Left:#%06x\nRight:#%06x' % (lc, rc))
        # sys.stdout.flush()
        

        self.frame_num += 1

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    halfwidth = camera.resolution[0]>>1
    camera.framerate = 30

    camera.zoom = (0.36, 0.52, 0.19, 0.19)
    camera.vflip = True
    camera.hflip = True


    with MyAnalysis(camera) as output:
        start = time.perf_counter()
        camera.start_recording(output, 'rgb')
        camera.wait_recording(86400)
        end = time.perf_counter()
        total_time = end-start
        sys.stdout.write('Time: %.2f' % total_time)
        sys.stdout.write('FPS: %.2f' % (output.frame_num / total_time))
        print("Done")