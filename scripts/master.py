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



    #sr80 = sr80()
    m = motorctrl(motor_com)
    v80 = Vertex80()
    
    
    
#    print('T=%f'%t)
#    m.limitsearch()
    m.motor.move_relative(m.angle_to_steps(+12))
    m.motor.move_relative(m.angle_to_steps(-180))
#   for tt in np.arange(20,110,10):
#        print('b1')
#        sr80.set_temperature(tt)
#        print('b2')
#        t = sr80.get_stability()
#        print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
#        while np.abs(t[0] - tt) > 0.01 and t[1] > 0.01:
#            time.sleep(10)
#            t = sr80.get_stability()
#            print('Wanted: %f; reached: %f; stability: %f'%(tt,t[0], t[1]))
#        time.sleep(2)
#        v80.measure(filename='BBSR80_%d.0'%tt)
    
#    sr80.set_temperature(100.0)
#    m.motor.move_relative(m.angle_to_steps(+180))
#    v80.measure(filename='BBIR563_100.0')
#    while t != 100.0:
#        time.sleep(1)
#        t = sr80.get_temperature()
#    m.motor.move_relative(m.angle_to_steps(-180))
#    v80.measure(filename='BBSR80_100.0')
#    print('T=%f'%t)
    sr80.set_temperature(20.0)
   
#   v80.measure()
    
