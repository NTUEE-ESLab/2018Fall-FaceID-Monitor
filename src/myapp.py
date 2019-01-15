#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from indicators import BeepThread, LedThread
import Rpi.GPIO as GPIO
import threading
from queue import Queue

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    # from camera import Camera
    # Raspberry Pi camera module (requires picamera package)
    from camera_opencv import Camera
    # from camera_pi import Camera


app = Flask(__name__)
appCam = Camera()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # return Response(gen(Camera()),
    return Response(gen(appCam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)

    # setup GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    pins = [19, 21, 23, 11]
    for p in pins:
        GPIO.setup(p, PIN.OUT)

    rgb = [GPIO.PWM(19, 50), GPIO.PWM(23, 50), GPIO.PWM(21, 50)]
    for c in rgb:
        c.start(0)
        c.ChangeDutyCycle(100)

    quitEvent = threading.Event()

    beepEvent = threading.Event()
    beepThread = BeepThread([beepEvent, quitEvent, [11], 3])
    beepThread.start()

    color = Queue()
    ledEvent = threading.Event()
    ledThread = LedThread([ledEvent, quitEvent, rgb, 3, color])
    ledThread.start()
