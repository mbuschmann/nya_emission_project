from serial import Serial
from time import sleep
import pyTMCL
import sys

class motorctrl():
    '''Motor control class for a Pandrive PD-1140 usb connected stepper motor. This class provides three methods to position the motor: .roof(), .blackbody() and .park()\n\n The motor needs to be set up with a left end switch configuration. Positions are:\n\t blackbody = left_end_switch - 180 deg\n\t roof = left_end_switch - 90 deg\n\t park = left_end_switch - 270 deg'''
    def angle_to_steps(self, angle):
        return int(angle * 256 / 1.8)

    def limitsearch(self):
        if not self.blockmotorcomm:
            print('Searching for left limit switch...')
            self.motor.send(13,0,0,0)
            a = 1
            while a!=0:
                sleep(1)
                a = self.motor.send(13,2,0,0).value
            #motor.reference_search(1)
            #sleep(16)
            #self.motor.stop()
            self.position = 'lim'
            print('Motor limit switch reached.')
        else:
            print('Motor not initialized: Motor communication blocked!')

    def resetstdbycurent(self):
        if not self.blockmotorcomm:
            print('Setting standby current')
            self.motor.set_axis_parameter(7,70); sleep(0.2)
        else: pass

    def setquiet(self):
        if not self.blockmotorcomm:
            print('Setting standby current')
            self.motor.set_axis_parameter(7,10); sleep(0.2)
        else: pass

    def movetoposition(self, pn):
        if not self.blockmotorcomm:
            p = self.position
            self.motor.stop()
            #self.resetstdbycurent()
            if not self.initdone:
                print('Moving from '+p+' to '+pn)
            else: pass
            pa = self.angles[self.targets.index(p)]
            pna = self.angles[self.targets.index(pn)]
            pm = pna-pa
            #if p=='lim' and pn=='roof':
            #    pos = self.d_lim_roof
            #elif p=='lim' and pn=='bb':
            #    pos = self.d_lim_bb
            #elif p=='lim' and pn=='park':
            #    pos = self.d_lim_park
            #elif p=='roof' and pn=='bb':
            #    pos = self.d_lim_bb-self.d_lim_roof
            #elif p=='roof' and pn=='park':
            #    pos = self.d_lim_park-self.d_lim_roof
            #elif  p=='bb' and pn=='park':
            #    pos = self.d_lim_park-self.d_lim_bb
            #elif  p=='bb' and pn=='roof':
            #    pos = -(self.d_lim_bb-self.d_lim_roof)
            #elif  p=='park' and pn=='bb':
            #    pos = -(self.d_lim_park-self.d_lim_bb)
            #elif  p=='park' and pn=='roof':
            #    pos = -(self.d_lim_park-self.d_lim_roof)
            #else:
            #    pos = 0
            self.motor.move_relative(self.angle_to_steps(pm))
            print('Moved to motor position:', pn)
            sleep(3)
            self.motor.stop()
            #self.setquiet()
            self.position = pn
        else:
            print('Not moving motor: Communication blocked.')

    def shutdown(self):
        print('Shut down sequence')
        if not self.blockmotorcomm:
            if self.position == 'park':
                self.serial_port.close()
            else:
                self.movetoposition('park')
                self.serial_port.close()

    #def roof(self):
    #    self.movetoposition('roof')

    #def blackbody(self):
    #    self.movetoposition('bb')

    #def park(self):
    #    self.movetoposition('park')

    def calibrate(self):
        print('Calibration procedure:\n\t Enter degrees to move to position\n\n Finish by entering "x". Printing out final position')
        s = ''
        ii = 0
        while s!='x':
            s = input('Input:')
            if s=='x':
                print('Final degrees:', ii)
            else:
                try:
                    i = float(s)
                    ii+=i
                    if not self.blockmotorcomm:
                        self.motor.move_relative(self.angle_to_steps(i))
                    else: pass
                except ValueError:
                    s=''
                else:
                    s=''
        return ii

    def init_motor(self):
        if not self.blockmotorcomm:
            print('Setting max speed')
            self.motor.set_axis_parameter(4,1000); sleep(0.2)
            print('Setting max acceleration')
            self.motor.set_axis_parameter(5,1000); sleep(0.2)
            print('Setting max current')
            self.motor.set_axis_parameter(6,100); sleep(0.2)
            print('Setting standby current')
            self.motor.set_axis_parameter(7,10); sleep(0.2)
            print('Setting microsteps')
            self.motor.set_axis_parameter(140,8); sleep(0.2)
            print('Setting freewheeling time limit')
            self.motor.set_axis_parameter(204,100); sleep(0.2)
            print('Setting reference search to left switch only')
            self.motor.set_axis_parameter(193,1); sleep(0.2)
            print('Setting reference search speed')
            self.motor.set_axis_parameter(194,200); sleep(0.2)
            print('Initialising ...')
            self.motor.move_relative(self.angle_to_steps(-20))
            self.limitsearch()
    #        self.movetoposition('bb')
    #        self.movetoposition('roof')
    #        self.movetoposition('park')
        else:
            print('Blocked communication with motor controller')
        self.initdone = True

    def __init__(self, comport, blockcomm=False):
        self.blockmotorcomm = blockcomm
        self.targets = ['lim', 'park', 'roof', 'sr800', 'ht', 'rt']
        self.angles = [0.0, 8.0, -163, -253, -119, -30.0]
        self.comport = comport
        self.MODULE_ADDRESS = 1
        if not self.blockmotorcomm:
            self.serial_port = Serial(self.comport)
            self.bus = pyTMCL.connect(self.serial_port)
            self.motor = self.bus.get_motor(self.MODULE_ADDRESS)
            self.motor.stop()
        #self.d_lim_park = -250.0
        #self.d_lim_bb = -164.0
        #self.d_lim_roof = -71.0
        self.initdone = False
        self.position = 'lim'
        self.init_motor()
        print('Ready.')

if __name__=='__main__':
    if sys.platform.startswith('win'):
        comport = "com3"
    elif sys.platform.startswith('linux'):
        comport = "/dev/ttyACM1"
    m = motorctrl(comport)
    #m.blackbody()
    #sleep(2)
    #m.park()
    #sleep(2)
    #m.roof()
    #m.shutdown()
    m.limitsearch()
    m.calibrate()
    #m.movetoposition('sr800')
    #m.motor.move_relative(m.angle_to_steps(-2))