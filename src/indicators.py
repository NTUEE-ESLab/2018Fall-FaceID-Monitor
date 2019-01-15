import threading
import RPi.GPIO as GPIO
from queue import Queue
import os
import sys
import time
class Indicator:
    def __init__(self):
        # setup GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        pins = [19, 21, 23, 11] 
        for p in pins:
            GPIO.setup(p, GPIO.OUT)
        GPIO.output(11, GPIO.LOW)

        self.rgb = [GPIO.PWM(19, 50), GPIO.PWM(23, 50), GPIO.PWM(21, 50)]
        for c in self.rgb:
            c.start(0)
            c.ChangeDutyCycle(100)

        self.quitEvent = threading.Event()

        self.beepEvent = threading.Event()
        self.beepmsg = Queue()
        self.beepThread = BeepThread([self.beepEvent, self.quitEvent, [11], self.beepmsg]) 
        self.beepThread.start()

        self.ledmsg = Queue()
        self.ledEvent = threading.Event()
        self.ledThread = LedThread([self.ledEvent, self.quitEvent, self.rgb, self.ledmsg])
        self.ledThread.start()

    def stop(self):
        self.quitEvent.set()
        self.beepEvent.set()
        self.ledEvent.set()
    
    def __del__(self):
        print('Destructor is called ...', file=sys.stderr)
        self.quitEvent.set()
        self.beepEvent.set()
        self.ledEvent.set()

        # self.beepThread.join(3.0)
        # self.ledThread.join(3.0)

        for c in self.rgb:
            c.stop()
        GPIO.cleanup()

    def beep(self, freq):
        self.beepmsg.put(freq)
        self.beepEvent.set()
    def led(self, color, freq):
        self.ledmsg.put({'color': color, 'freq': freq})
        self.ledEvent.set()
        '''
        if freq != 0:
            self.ledmsg.put({'r':color[0], 'g':color[1], 'b':color[2], 'freq':freq})
            self.ledEvent.set() 
        else:
            self.ledEvent.clear()
            for i in range(3):
                dc = int((255 - color[i]) * 100 / 255)
                self.rgb[i].ChangeDutyCycle(dc)
        '''
    


class MyThread(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.event = args[0]
        self.quit = args[1]
        self.pins = args[2]
        self.msg = args[3]
        self.daemon = True

class BeepThread(MyThread):
    '''
    def __init__(self, args):
        super().__init__(args)
    '''
    def run(self):
        freq = 0
        while not self.quit.is_set():
            while not self.msg.empty():
                freq = self.msg.get()
                self.event.clear()
            if freq == 0:
                self.event.wait()
                continue
            while not self.event.is_set() and not self.quit.is_set():
                breaktime = 1.0 / (freq * 2)
                GPIO.output(self.pins[0], GPIO.HIGH)
                time.sleep(breaktime)
                GPIO.output(self.pins[0], GPIO.LOW)
                time.sleep(breaktime)

class LedThread(MyThread):
    '''
    def __init__(self, args):
        super().__init__(args)
    '''
    def setColor(self, color):
        for i in range(3):
            dc = int((255 - color[i])*100 / 255)
            self.pins[i].ChangeDutyCycle(dc)
    def run(self):
        freq = 0
        color = [0, 0, 0]
        while not self.quit.is_set():
            while not self.msg.empty():
                msg = self.msg.get()
                color = msg['color']
                freq = msg['freq']
                self.setColor(color)
                self.event.clear()
            if freq == 0:
                self.event.wait()
                continue
            while not self.event.is_set() and not self.quit.is_set():
                self.setColor(color)
                breaktime = 1.0 / (freq * 2)
                time.sleep(breaktime)
                self.setColor([0,0,0])
                time.sleep(breaktime)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    pins = [19, 21, 23, 11]
    for p in pins:
        GPIO.setup(p, GPIO.OUT)

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

    while True:
        cmd = input('Enter cmd: ')
        cmds = cmd.split(' ')
        if cmds[0] == 'quit':
            quitEvent.set()
            beepEvent.set()
            ledEvent.set()
            beepThread.join()
            ledThread.join()
            for c in rgb:
                c.stop()
            GPIO.cleanup()
            exit(0)
        elif cmds[0] == 'beep': 
            if beepEvent.is_set():
                beepEvent.clear()
            else:
                beepEvent.set()

        elif cmds[0] == 'led':
            cmds = cmd.split(' ')
            if len(cmds) == 1:
                ledEvent.clear()
            else:
                r,g,b = int(cmds[1]), int(cmds[2]), int(cmds[3].strip())
                logging.debug(r,g,b)
                color.put([r,g,b])
                ledEvent.set()
