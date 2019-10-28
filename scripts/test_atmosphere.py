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

    output_direc = os.path.join('output', 'test4')

    logfile = open(os.path.join(output_direc, 'logfile.txt'), 'w')

    

    sr80 = sr80()
    m = motorctrl(motor_com)
    time.sleep(1)
    v80 = Vertex80()

    m.motor.move_relative(m.angle_to_steps(+12))
    time.sleep(2)
    tt = 20.0
    sr80.set_temperature(tt)
    t = sr80.get_stability()
    print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
    
    while np.abs(t[0] - tt) > 0.01 or t[1] > 0.01:
        time.sleep(10)
        t = sr80.get_stability()
        print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
        time.sleep(2)

    sr80.start_twatch()
    v80.measure(filename=os.path.join(output_direc,'BBSR80_%d.0'%tt))
    tmean, tstd = sr80.stop_twatch()
    logfile.write('%s %e %e\n'%('BBSR80_%d.0'%tt, tmean, tstd))

    tt = 100.0
    sr80.set_temperature(tt)
    m.motor.move_relative(m.angle_to_steps(-170))
    time.sleep(2)
    v80.measure(filename=os.path.join(output_direc,'Atmo.0'))
    logfile.write('%s\n'%'atmo.0')
    v80.measure(filename=os.path.join(output_direc,'Atmo.1'))
    logfile.write('%s\n'%'atmo.1')
    while np.abs(t[0] - tt) > 0.01 or t[1] > 0.01:
        time.sleep(10)
        t = sr80.get_stability()
        print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
        time.sleep(2)
    
    m.motor.move_relative(m.angle_to_steps(+170))
    sr80.start_twatch()
    v80.measure(filename=os.path.join(output_direc,'BBSR80_%d.0'%tt))
    tmean, tstd = sr80.stop_twatch()
    logfile.write('%s %e %e\n'%('BBSR80_%d.0'%tt, tmean, tstd))
    logfile.close()
    sr80.set_temperature(30.0)
    time.sleep(1)
    del sr80
    del v80
    del m
    
