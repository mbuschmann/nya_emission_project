from __future__ import print_function, division
from serial import Serial
from time import sleep
import numpy as np
import time, sys

class hutchsensor():
    '''Class to read the hutch status from an Arduino Nano.'''
    def _gethutchstatusserial(self):
        a = self.serial.readline()
        self.hutchstatusvar = a.decode('utf-8').split(' ')[1].strip()
        self.voltage = float(a.decode('utf-8').split(' ')[0].strip())
        self._t = time.time()

    def hutchstatus(self):
        if (time.time()-self._t)>0.5:
            self._gethutchstatusserial()
            return self.hutchstatusvar
        else: pass

    def __init__(self, comport):
        self.comport = comport
        self.nofsensors = 4
        self.serial = Serial(self.comport)
        self.serial.flushInput()
        self._gethutchstatusserial()

if __name__=='__main__':
    if sys.platform.startswith('win'):
        comport = "com1"
    elif sys.platform.startswith('linux'):
        comport = "/dev/ttyUSB0"
    hsens = hutchsensor(comport)
    for i in range(100):
        print(hsens.hutchstatus())
        time.sleep(1)
