import cv2
from base_camera import BaseCamera
from motion_detection_api import MotionDetection
from indicators import Indicator
import RPi.GPIO as GPIO
from face_api import FaceDetection
import sys
from datetime import datetime
import os
import time

ALARM_BUFFER = 10
AUTH_BUFFER = 10
ALARM_DURATION = 30

class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        print('Starting camera ...')
        width = 640
        height = 480
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        indicator = Indicator()
        md = MotionDetection(threshold=2500, weight=0.08)
        fd = FaceDetection()
        PicDir = ''
        savePics = []
        isAlarm = False
        mailSent = False
        lastMove = lastAuth = lastAlarm = time.time()
        global MOTION_BUFFER
        global FACE_BUFFER
        global ALARM_DURATION
        
        while True:
            # read current frame
            _, img = camera.read()
            # img = cv2.resize(img, (320, 240))
            now = time.time()
            timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')

            # Motion Detection: not ( (now-lastAuth<FACE_BUFFER) or (lastMove>lastAuth))
            if now-lastAuth>AUTH_BUFFER and lastMove<=lastAuth:
                indicator.led([0, 0, 255], 1)
                print('[{0}] Detecting motion ...'.format(timestamp))
                img, motion = md.motionDetect(img)
                if motion:
                    print('[{0}] Motion detected !!'.format(timestamp))
                    lastMove = now
                    indicator.led([255,255,0], 2)
            else:
                md.updateFrame(img)

            # Face Detection: (now-lastAuth>FACE_BUFFER) and (lastMove > lastAuth)
            if now-lastAuth>AUTH_BUFFER and lastMove>lastAuth:
                img, names = fd.detect(img)
                print('[{0}] Detecting face ...'.format(timestamp))
                if 'Mike' in names:
                    print('[{0}] Authentication passed'.format(timestamp))
                    lastAuth = now
                    savePics.clear()
                    mailSent = False
                    indicator.led([0,255,0], 0)
                    if isAlarm:
                        indicator.beep(0)
                        isAlarm = False

            # Backup frame: lastMove>lastAuth and not mailSent
            if lastMove>lastAuth and not mailSent:
                savePics.append((timestamp, img))

            # Alarm: now-lastMove>ALARM_BUFFER and lastMove>lastAuth
            if now-lastMove>ALARM_BUFFER and lastMove>lastAuth:
                if not isAlarm:
                    indicator.led([255,0,0], 4)
                    indicator.beep(3)
                    isAlarm = True
                if not mailSent:
                    print('[{0}] Saving alarm pics ...'.format(timestamp), end='')
                    os.mkdir(timestamp)
                    for tm, pic in savePics:
                        path = '{0}/{1}.JPG'.format(timestamp, tm)
                        cv2.imwrite(path, pic)
                    os.system('sh mail.sh {0}'.format(timestamp))
                    print('done')
                    mailSent = True
            if now-lastAlarm>ALARM_DURATION:
                lastAuth = lastMove = lastAlarm = now
                indicator.led([0,255,0], 0)
                indicator.beep(0)
                savePics.clear()
                isAlarm = False
                mailSent = False
                lastMove = lastAuth = lastAlarm = time.time()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
