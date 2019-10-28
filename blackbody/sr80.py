import sys, os
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
try:
    scriptpath = os.path.dirname(os.path.abspath(__file__))
except:
    scriptpath = os.getcwd()
    sys.path.append(scriptpath)
sys.path.append(os.path.join(scriptpath, 'blackbody'))
from prologixx import PrologixGPIBEthernet
from time import sleep, time
from multiprocessing import Process, Manager

class sr80():
    def logtemps(self):
        logfile = os.path.join('Z:\\out\\tlogs', dt.datetime.now().strftime('%Y%m%d') + '_sr80_targets.dat')
        tempheader = 'Logfile of SR80 temperature\n\n\n\n'
        tempheader += 'date time T_sr80\n'
        self.temp = self.get_temperature()
        self._datetime = dt.datetime.now()
        if not os.path.exists(logfile):
            with open(logfile, 'a') as f:
                f.write(tempheader)
                f.write(self._datetime.strftime('%Y%m%d %H:%M:%S ') + '%3.4f\n'%self.temp)
        else:
            with open(logfile, 'a') as f:
                f.write(self._datetime.strftime('%Y%m%d %H:%M:%S ') + '%3.4f\n'%self.temp)

    def readini(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../blackbody', 'sr80.ini'), 'r') as f:
            inil = f.readlines()
        self.ini = {}
        for l in inil:
            if l.strip() != '':
                ll = l.split('=')
                self.ini[ll[0].strip()] = ll[1].strip()
            else: pass

    def __init__(self, blockcomm = False):
        self.blocksr80comm = blockcomm
        if not self.blocksr80comm:
            self.host = '172.18.0.130'
            self.gpib_addr = 10
            #self.readini
            self.pr = PrologixGPIBEthernet(self.host, timeout=1)
            self.pr.connect()
            self.pr.write('++addr %d'%self.gpib_addr)
            print (self.pr.query('++ver'))
            #m = Manager()
            #self.stat = m.dict()
            #self.stat['r_mean'] = -1.0
            #self.stat['r_std'] = -1.0
            #self.stat['r_valid'] = False
            #self.stat['MEAS'] = False
            #sleep(1)
            #self.watch_t = Process(target=self.watch_sr80, args=(self.stat,))
            #self.watch_t.start()

    #def __del__(self):
    #    self.watch_t.terminate()
    #    self.watch_t.join()
    #    self.watch_t.close()
    #    self.pr.close()

    #def start_twatch(self):
    #    self.stat['MEAS'] = True

    #def stop_twatch(self):
    #    self.stat['MEAS'] = False
    #    sleep(1)
    #    return(self.stat['l_mean'], self.stat['l_std'])

    #def watch_sr80(self,stat):
    #    ts = [0,0,0,0,0,0,0,0,0,0,0]
    #    nr = 0
    #    nr_meas = 0
    #    l_mean = 0
    #    l_std = 0
    #    stat['r_valid'] = False
    #    while True:
    #        sleep(1)
    #        t = self.get_temperature()
    #        if t == -999.0:
    #            continue
    #        ts.pop(0)
    #        ts.append(t)
    #        if nr < 11:
    #            nr += 1
    #            stat['r_mean'] = -1
    #            stat['r_std'] = -1
    #            stat['r_valid'] = False
    #            r_std = -1
    #            continue
    #        r_mean = np.mean(np.array(ts))
    #        r_std = np.std(np.array(ts))
    #        if stat['MEAS']:
    #            nr_meas += 1
    #            l_mean += t
    #            l_std += t*t
    #        if nr_meas > 0 and not stat['MEAS']:
    #            stat['l_mean'] = l_mean / nr_meas
    #            stat['l_std'] = l_std / nr_meas - stat['l_mean']*stat['l_mean']
    #            nr_meas = 0
    #            l_mean = 0
    #            l_std = 0
    #        stat['r_mean'] = r_mean
    #        stat['r_std'] = r_std
    #        stat['r_valid'] = True

    #def get_stability(self):
    #    return (self.stat['r_mean'], self.stat['r_std'],self.stat['r_valid'])

    def reconnect(self):
        if not self.blocksr80comm:
            self.pr.close()
        sleep(1)
        self.__init__()

    def set_temperature(self, temp):
        if not self.blocksr80comm:
            self.pr.write('ST%f'%temp)
        else:
            print('Setting SR80 temperature currently disabled.')

    def get_temperature(self):
        if not self.blocksr80comm:
            tem = self.pr.query('RE')
            sleep(1)
        else: pass
        try:
            tem = float(tem)
        except:
            tem = -999
        return(tem)

if __name__=='__main__':
    if len(sys.argv)<2:
        print('Usage:\n\t $ python sr80.py <arg>\n\n where <arg> is e.g. "30min", "openend" or "plot logfilefolder"')
    else:
        arg = sys.argv[1]
        if arg == 'plot':
            fig, ax = plt.subplots(1)
            ax.set_ylabel('Temperature [°C]')
            for f in os.listdir(sys.argv[2]):
                if f.endswith('sr80_targets.dat'):
                    try:
                        temps = np.recfromtxt(os.path.join(sys.argv[2], f), skip_header=4, names=True, encoding='utf8', delimiter=' ')
                        datetimes = [dt.datetime.strptime(str(i)+str(j), '%Y%m%d%H:%M:%S') for i,j in zip(temps['date'], temps['time'])]
                        ax.plot(datetimes, temps['T_sr80'], '.')
                    except Exception as e:
                        print(e)
                        pass
            fig.autofmt_xdate()
            plt.show()
        else:
            bb = sr80()
            tt = dt.datetime.now()
            #print(bb.tempheader)
            if sys.argv[1].strip() == 'openend':
                while True:
                    bb.logtemps()
                    print(bb._datetime, bb.temp)
                    sleep(5)
            else:
                while dt.datetime.now()< tt+dt.timedelta(minutes=int(sys.argv[1].strip('min'))):
                    bb.logtemps()
                    print(bb._datetime, bb.temp)
                    sleep(5)
            del bb