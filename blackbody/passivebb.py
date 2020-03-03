from __future__ import print_function, division
from serial import Serial
from time import sleep
import numpy as np
import time, sys, os
import datetime as dt
import matplotlib.pyplot as plt

class passivebb():
    '''Class to get the mean temperature from a Serial connection to Arduino Nano.'''
    def logtemps(self):
        logfile = os.path.join('Z:\\out\\tlogs', dt.datetime.now().strftime('%Y%m%d') + '_bb_targets.dat')
        tempheader = 'Arduino Nano readout of 2 x 4 DS18B20 temperature sensors of room-\n'
        tempheader += 'temperature blackbody target (T_rt) and hot blackbody target (T_ht).\n'
        tempheader += 'Plus one voltage readout of thermistor on hot blackbody target (V_ht)\n\n'
        tempheader += 'date time T_ht_left T_ht_right T_ht_bottom T_ht_top V_ht T_rt_topright T_rt_topleft T_rt_bottomleft T_rt_bottomright\n'
        self.gettemps()
        if not os.path.exists(logfile):
            with open(logfile, 'a') as f:
                f.write(tempheader)
                f.write(self._datetime.strftime('%Y%m%d %H:%M:%S ') + self.temperatures+'\n')
        else:
            with open(logfile, 'a') as f:
                f.write(self._datetime.strftime('%Y%m%d %H:%M:%S ')+self.temperatures+'\n')

    def gettemps(self):
        self.serial.flush()
        a = self.serial.read_all().splitlines()
        n = 0
        try:
            n+=1
            if len(a) > 0:
                a = a[-1]
            #print(a)
            self.temperatures = a.decode('utf-8')
            self._datetime = dt.datetime.now()
            n = 0
        except:
            if n<10:
                sleep(0.5)
                self.gettemps()
            else:
                raise RuntimeError('Did not get response from Passice BB Arduino after '+str(n)+' tries...')

    def get_rt_temp(self):
        self.gettemps()
        return self._datetime.strftime('%Y%m%d %H:%M:%S ') + self.temperatures[29:]

    def get_ht_temp(self):
        self.gettemps()
        return self._datetime.strftime('%Y%m%d %H:%M:%S ') + self.temperatures[:28]

    def __init__(self, comport):
        self.comport = comport
        self.serial = Serial(self.comport)
        #self.serial.flushInput()
        self.serial.flushOutput()
        self.gettemps()

if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage:\n\t $ python all_bb_temp_test.py <arg>\n\n where <arg> is e.g. "30min" or "plot logfilefolder"')
    else:
        arg = sys.argv[1]
        if arg == 'plot':
            fig, ax = plt.subplots(1)
            ax.set_ylabel('Temperature [°C]')
            for f in os.listdir(sys.argv[2]):
                if f.endswith('bb_targets.dat'):
                    try:
                        print(f)
                        temps = np.recfromtxt(os.path.join(sys.argv[2], f), skip_header=4, names=True, encoding='utf8', delimiter=' ')
                        datetimes = [dt.datetime.strptime(str(i)+str(j), '%Y%m%d%H:%M:%S') for i,j in zip(temps['date'], temps['time'])]
                        c = ['k', 'r', 'g', 'b', 'purple', 'y', 'cyan', 'magenta']
                        for i, key in enumerate(['T_ht_left', 'T_ht_right', 'T_ht_bottom', 'T_ht_top', 'T_rt_topright', 'T_rt_topleft', 'T_rt_bottomleft', 'T_rt_bottomright']):
                            ax.plot(datetimes, temps[key], '.', color=c[i])
                    except Exception as e:
                        print(e)
                        pass
            fig.autofmt_xdate()
            plt.show()
        else:
            if sys.platform.startswith('win'):
                comport = "com6"
            elif sys.platform.startswith('linux'):
                comport = "/dev/ttyUSB1"
            pbb = passivebb(comport)
            tt = dt.datetime.now()
            #print(pbb.tempheader)
            if sys.argv[1].strip() == 'openend':
                while True:
                    pbb.logtemps()
                    print(pbb._datetime, pbb.temperatures.strip())
                    time.sleep(5)
            else:
                while dt.datetime.now()< tt+dt.timedelta(minutes=int(sys.argv[1].strip('min'))):
                    pbb.logtemps()
                    print(pbb._datetime, pbb.temperatures.strip())
                    time.sleep(5)
