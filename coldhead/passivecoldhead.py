from __future__ import print_function, division
from serial import Serial
from time import sleep
import numpy as np
import time, sys

class passivecoldhead():
    '''Class to get the mean temperature from a Serial connection to Arduino Nano.'''
    def gettemps(self):
        a = self.serial.readline()
        self.temperatures = [float(a[i:i+5].decode('utf-8')) for i in [0,6,12,18]]
        self._t = time.time()
        
    def mean_temp(self):
        if (time.time()-self._t)>1:
            self.gettemps()
        else: pass
        return np.mean(self.temperatures)
        
    def std_temp(self):
        if (time.time()-self._t)>1:
            self.gettemps()
        else: pass
        return np.std(self.temperatures)

    def gettemp(self, i):
        if (time.time()-self._t)>1:
            self.gettemps()
        else: pass
        if np.abs(i)<self.nofsensors:
            return self.temperatures[i]
        else:
            return -99.0
        
    def __init__(self, comport):
        self.comport = comport
        self.nofsensors = 4
        self.serial = Serial(self.comport)
        self.serial.flushInput()
        self.gettemps()

if __name__=='__main__':
    if sys.platform.startswith('win'):
        comport = "com3"
    elif sys.platform.startswith('linux'):
        comport = "/dev/ttyUSB1"
    pch = passivecoldhead(comport)    
    for i in range(100):
        print(pch.gettemp(0), pch.gettemp(1), pch.gettemp(2), pch.gettemp(3))
        print(pch.mean_temp(), '+-', pch.std_temp())
        print('............')
        time.sleep(1)
