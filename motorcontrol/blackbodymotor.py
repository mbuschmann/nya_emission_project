from __future__ import print_function, division
from serial import Serial
from time import sleep
import sys, struct
from importlib import reload


class BlackBodyMotor():
    
    def mys(self, tu):
        s=0
        for i in tu[:-1]:
            s+=i
        for i in struct.pack('I', tu[-1]):
            #s+=struct.unpack('B', bytes(i))[0]
            s+=i
            if s>256:
                s-=256
        return s

    def sendrec(self, command, par, val):
        c = self.mys((self.address, command, par, self.motorbank, val))
        msg = struct.pack(self._MSG_STRUCTURE, self.address, command, par, self.motorbank, val, c)
        self.serial.write(msg)
        m = self.serial.read_all()
        sleep(1)
        try:
            return struct.unpack(self._MSG_STRUCTURE, m)
        except:
            return m

    def save_current_position(self, coordnumber):
        command = 32
        par = coordnumber
        val = 0
        m = self.sendrec(command, par, val)
        return m

    def store_coordinate(self, coordnumber, pos):
        command = 30
        par = coordnumber
        val = pos
        return self.sendrec(command, par, val)
        
    def wait_for_target_position(self, par=1):
        command = 27
        val = 0
        return self.sendrec(command, par, val)

    def search_left_limit(self):
        command = 13
        par = 0
        val = 0
        m = self.sendrec(command, par, val)
        print(m)
        #self.wait_for_target_position(par=4)
        m = self.save_current_position(self.leftswitchcoordnb)
        print(m)
        return m

    def stop(self):
        command = 28
        par, val = 0,0
        return self.sendrec(command, par, val)

    def shutdown(self):
        sleep(1)
        self.serial.close()

    def point_to_bb(self):
        command = 4
        par = 2
        val = self.bbcoordnb
        m = self.sendrec(command, par, val)
        #self.wait_for_target_position()
        return m

    def point_to_roof(self):
        command = 4
        par = 2
        val = self.roofcoordnb
        m = self.sendrec(command, par, val)
        #self.wait_for_target_position()
        return m

    def move_to_rel_position(self, pos=0):
        command = 32
        par = 1
        val = pos
        m = self.sendrec(command, par, val)
        #self.wait_for_target_position()
        return m

    def move_to_abs_position(self, pos=0):
        command = 32
        par = 0
        val = pos
        m = self.sendrec(command, par, val)
        #self.wait_for_target_position()
        return m

    def init_axis_params(self):
        # maximum positioning speed
        m = self.sendrec(5, 4, 200)
        sleep(0.2)
        try:
            print('Setting max speed', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
        # maximum acceleration
        m = self.sendrec(5, 5, 200)
        sleep(0.2)
        try:
            print('setting max acceleration', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
        # maximum current
        m = self.sendrec(5, 6, 10)
        sleep(0.2)
        try:
            print('Setting max current', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
        # standby current
        m = self.sendrec(5, 7, 10)
        sleep(0.2)
        try:
            print('Setting standby current', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
        # set microsteps
        m = self.sendrec(5, 140, 8)
        sleep(0.2)
        try:
            print('Setting microsteps', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
        # set reference search
        m = self.sendrec(5, 193, 1)
        sleep(0.2)
        try:
            print('Setting reference search', struct.unpack(self._MSG_STRUCTURE, m))
        except: 
            print('Setting max speed', m)
    
        
        

    def __init__(self, comport='/dev/ttyACM0'):
        print('Initialising ...')
        self.roofcoordnb = 1
        self.bbcoordnb = 2
        self.leftswitchcoordnb = 3
        self.rightswitchcoordnb = 4
        self.steps_to_bb = 200*256
        self.steps_to_roof = 100*256        
        self.serial = Serial(comport)
        self._MSG_STRUCTURE = ">BBBBIB"
        self.address = 1
        self.motorbank = 0
        self.init_axis_params()
        print('Done.\n Starting left limit switch search...')
        self.search_left_limit()
        sleep(10)
        #print('Moving to black body position...')
        #print(self.move_to_rel_position(pos=self.steps_to_bb))
        #print(self.save_current_position(self.bbcoordnb))
        #print('Moving to roof position...')
        #self.move_to_rel_position(pos=self.steps_to_roof)
        #self.save_current_position(self.roofcoordnb)
        self.stop()

        
if __name__=='__main__':
    if len(sys.argv)==2:
        if sys.argv[1]=='roof':
            B = BlackBodyMotor(comport)
            B.point_to_roof()
            B.shutdown()
            exit('Done.')
        elif sys.argv[1]=='bb':
            B = BlackBodyMotor()
            B.point_to_bb()
            B.shutdown()
            exit('Done.')
        else:
            exit('Usage:\n\t ./motor_control_4.py <target>\n\n target can be "roof" or "bb"')            
    else:
        exit('Usage:\n\t ./motor_control_4.py <target>\n\n target can be "roof" or "bb"')
 

"""

def mys(tu):
    s=0
    for i in tu[:-1]:
        s+=i
    for i in struct.pack('I', tu[-1]):
        #s+=struct.unpack('B', bytes(i))[0]
        s+=i
        if s>256:
            s-=256
    return s
    
def sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val):
    c = mys((address, command, par, motorbank, val))
    msg = struct.pack(MSG_STRUCTURE, address, command, par, motorbank, val, c)
    serial.write(msg)
    m = serial.read_all()
    try:
        return struct.unpack(MSG_STRUCTURE, m)
    except:
        return m

serial = Serial('/dev/ttyACM0')

MSG_STRUCTURE = ">BBBBIB"

address = 1
motorbank = 0

# set parameter for reference search left limit switch only
command = 5
par = 193
val = 1
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)


# get axis parameter for left limit switch status
command = 6
par = 11
val = 0
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)

# reference search for left limit switch
command = 13
par = 0
val = 0
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)


# set no microsteps
command = 5
par = 140
val = 8
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)

# move to position
command = 4
par = 0
val = 50*256
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)

# copy all coordinates except 0 from RAM to EEPROM
command = 30
par = 0
val = 255
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)


# store current position to coordinate <par>
command = 32
par = 1
val = 0
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)


# move to coordinate <val>
command = 4
par = 2
val = 1
sendrec(serial, MSG_STRUCTURE, address, command, par, motorbank, val)

"""

