import cv2
import numpy as np
from imutils.video import FPS
import sys

class MotionDetection:
    def __init__(self, threshold=1600, weight=0.05):
        self.threshold = threshold
        self.prevFrame = None
        self.avg = None
        self.avg_float = None
        self.weight = 0.05
    def updateFrame(self, frame):
        self.prevFrame = frame
        self.avg = cv2.blur(frame, (4, 4))
        self.avg_float = np.float32(self.avg)
    def motionDetect(self, frame):
        if self.prevFrame is None:
            self.prevFrame = frame
            self.avg = cv2.blur(frame, (4, 4))
            self.avg_float = np.float32(self.avg)
            return frame, False

        blur = cv2.blur(frame, (4, 4))
        diff = cv2.absdiff(self.avg, blur)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        
        motion = False
        for c in cnts:
            if cv2.contourArea(c) < self.threshold:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion = True

        cv2.drawContours(frame, cnts, -1, (0, 255, 255), 2)


        cv2.accumulateWeighted(blur, self.avg_float, self.weight)
        self.avg = cv2.convertScaleAbs(self.avg_float)

        return frame, motion

