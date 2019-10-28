import requests,os,time,sys
scriptpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(scriptpath, 'motorcontrol'))
sys.path.append(os.path.join(scriptpath, 'blackbody'))
sys.path.append(os.path.join(scriptpath, 'vertex80'))
from blackbodymotor_pytmcl import motorctrl
from sr80 import sr80
from Vertex80 import Vertex80
import tkinter
import numpy as np

motor_com = "COM3"
stat_htm = 'http://10.10.0.1/stat.htm'



if __name__=='__main__':

    logfile = open('lin_test/logfile.txt', 'w')

    sr80 = sr80()
    m = motorctrl(motor_com)
    v80 = Vertex80()

    m.motor.move_relative(m.angle_to_steps(+12))
    m.motor.move_relative(m.angle_to_steps(-180))
    for tt in np.arange(20,30,10):
        sr80.set_temperature(tt)
        t = sr80.get_stability()
        print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
        while np.abs(t[0] - tt) > 0.01 or t[1] > 0.01:
            time.sleep(10)
            t = sr80.get_stability()
            print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
        time.sleep(2)
        sr80.start_twatch()
        v80.measure(filename=os.path.join('lin_test','BBSR80_%d.0'%tt))
        tmean, tstd = sr80.stop_twatch()
        logfile.write('%s %e %e\n'%('BBSR80_%d.0'%tt, tmean, tstd))
    sr80.set_temperature(20.0)
    logfile.close()
    del sr80
    del v80
    del m
    
