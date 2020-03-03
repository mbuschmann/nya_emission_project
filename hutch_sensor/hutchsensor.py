from __future__ import print_function, division
from serial import Serial
from time import sleep
import numpy as np
import time, sys

class hutchsensor():
    '''Class to read the hutch status from an Arduino Nano.'''
    def _gethutchstatusserial(self):
        self.serial.flush()
        a = self.serial.read_all().splitlines()
        self._t = time.time()
        try:
            if len(a) > 0:
                a = a[-1]
            l = a.decode('utf-8').split(' ')
            hutchstatusvar = dict(zip(l[::2], l[1::2]))
#            self.voltage = float(a.decode('utf-8').split(' ')[0].strip())
            self._t = time.time()
            if type(hutchstatusvar) == type(None):
                self.hutchstatusvar = {}
            else:
                self.hutchstatusvar = hutchstatusvar
        except:
            self.hutchstatusvar = {}

    def hutchstatus(self):
        if not self.valid:
            return({})

        if (time.time()-self._t)>0.5:
            self._gethutchstatusserial()
            
            return self.hutchstatusvar
        else:
            return({})
                
    def __init__(self, comport):
        self.comport = comport
        self.nofsensors = 4
        self.valid = True
#        try:
        self.serial = Serial(self.comport)
        self.serial.flushOutput()
        self._gethutchstatusserial()
#        except:
#            self.valid = False



if __name__=='__main__':
    if sys.platform.startswith('win'):
        comport = "com5"
    elif sys.platform.startswith('linux'):
        comport = "/dev/ttyUSB0"
    hsens = hutchsensor(comport)
    sleep(1)
    for i in range(1,1000):
        print(hsens.hutchstatus())
        sleep(1)
