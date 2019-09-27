import sys,os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../blackbody'))
from prologixx import PrologixGPIBEthernet
from time import sleep, time
from multiprocessing import Process, Manager

class sr80():
    def __init__(self):
        self.host = '172.18.0.130'
        self.gpib_addr = 10
        self.pr = PrologixGPIBEthernet(self.host)
        self.pr.connect()
        self.pr.write('++addr %d'%self.gpib_addr)
        print (self.pr.query('++ver'))
        m = Manager()
        self.stat = m.dict()
        self.stat['r_mean'] = -1.0
        self.stat['r_std'] = -1.0
        self.stat['r_valid'] = False
        self.stat['MEAS'] = False
        sleep(1)
        self.watch_t = Process(target=self.watch_sr80, args=(self.stat,))
        self.watch_t.start()
        
    def __del__(self):
        self.watch_t.terminate()
        self.watch_t.join()
        self.watch_t.close()
        self.pr.close()
 
    def start_twatch(self):
        self.stat['MEAS'] = True
        
    def stop_twatch(self):
        self.stat['MEAS'] = False
        sleep(1)
        return(self.stat['l_mean'], self.stat['l_std'])
        
    def watch_sr80(self,stat):
        ts = [0,0,0,0,0,0,0,0,0,0,0]
        nr = 0
        nr_meas = 0
        l_mean = 0
        l_std = 0
        stat['r_valid'] = False
        while True:
            sleep(1)
            t = self.get_temperature()
            if t == -999.0:
                continue
            ts.pop(0)
            ts.append(t)
            if nr < 11:
                nr += 1
                stat['r_mean'] = -1
                stat['r_std'] = -1
                stat['r_valid'] = False
                r_std = -1
                continue
            r_mean = np.mean(np.array(ts))
            r_std = np.std(np.array(ts))
            if stat['MEAS']:
                nr_meas += 1
                l_mean += t
                l_std += t*t
            if nr_meas > 0 and not stat['MEAS']:
                stat['l_mean'] = l_mean / nr_meas
                stat['l_std'] = l_std / nr_meas - stat['l_mean']*stat['l_mean']
                nr_meas = 0
                l_mean = 0
                l_std = 0
            stat['r_mean'] = r_mean
            stat['r_std'] = r_std
            stat['r_valid'] = True

    def get_stability(self):
        return (self.stat['r_mean'], self.stat['r_std'],self.stat['r_valid'])
 
    def reconnect(self):
        
        self.pr.close()
        sleep(1)
        self.__init__()
        
    def set_temperature(self, temp):
        self.pr.write('ST%f'%temp)
                
    def get_temperature(self):
        tem = self.pr.query('RE')
        sleep(1)
        try:
            tem = float(tem)
        except:
            tem = -999
        return(tem)
