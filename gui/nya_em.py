from __future__ import print_function, division
import os, sys, time
import datetime as dt
from PyQt5.QtGui import QIcon
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import requests
scriptpath = os.path.dirname(os.path.abspath(__file__))
print(scriptpath)
scriptpath = 'C:/Users/ftir/nya_emission_project'
sys.path.append(os.path.join(scriptpath, 'motorcontrol'))
sys.path.append(os.path.join(scriptpath, 'blackbody'))
sys.path.append(os.path.join(scriptpath, 'vertex80'))
sys.path.append(os.path.join(scriptpath, 'gui'))
sys.path.append(os.path.join(scriptpath, '..', 'ftsreader'))
from blackbodymotor_pytmcl import motorctrl
#from sr80 import sr80
from sr800 import sr800
from Vertex80 import Vertex80
from hutchsensor import hutchsensor
from ftsreader import ftsreader
from brennenstuhl import brennenstuhl
import logging

class NyaEM():
    def __init__(self, folder='Z:/out/'):
        super().__init__()

        logfile = dt.datetime.strftime(dt.datetime.now(), 'z:\\log\\%Y%m%d.log')
        logging.basicConfig(filename=logfile,format='%(asctime)s %(message)s')
        logging.warning('Starting nya_em.py')

        self.preset_temps = {'ir301': 120.0,
                             'ht': 0.0,
                             'lim':0.0}

        self.folder = os.path.abspath(folder)
        self.sequence_file = 'z:\\in\\routine_measurement.txt'
        self.meas_start_time = dt.datetime.now()
        #
        if sys.platform.startswith('win'):
            self.motor_com = "COM3"
            self.hutch_com = "COM5"
        elif sys.platform.startswith('linux'):
            self.motor_com = "/dev/ttyACM1"
        self.stat_htm = 'http://172.18.0.110/stat.htm'

        #
        self.initinstruments()
        #
        self.act_filename = ''
        self.last_meas_file = ''
        # Variable used by run_sequence()
        self.entry = 1  # start always at the beginning of the sequence

        self.actual_job = 'idle' # 'run sequence'
        self.run_seq = False # True if a sequence is running
        self.conditions_ok = False # True if the conditions for measurement are fulfilled.
        self.act_entry = 1 # contains the number of the entry worked on
        self.pka = -1

        self.measurement = False # True if a measurement is under way
        self.measurement_repeat = False
        self.wait = False # True if a wait statement is active
        self.time_continue = dt.datetime.now() # initialize timer variable, this is used in the wait time
        self.new_measurement = False

        self.hutchstatus = {}

        # Conditions for measurement
        self.condition_hutch = False
        self.condition_v80 = True
		
        self.bbtemp = -1


        self.load_sequence(self.sequence_file)


    def load_sequence(self, file):
        with open(file, 'r') as fid:
            read_seq = False
            read_con = False
            read_v80 = False
            nr = 1
            self.sequence = {}
            for l in fid:
                if l.strip == '':
                    continue
                if l.strip() == 'sequence':
                    read_seq = True
                    read_con = False
                    read_v80 = False
                    nr = 1
                    continue
                if l.strip() == '':
                    read_seq = False
                    read_con = False
                    read_v80 = False
                elif l.strip() == 'v80 parms':
                    read_seq = False
                    read_con = False
                    read_v80 = True
                    continue
                elif l.strip() == 'meas conditions':
                    read_seq = False
                    read_con = True
                    read_v80 = False
                    nr = 1
                    continue
                if read_seq:
                    self.sequence[nr] = l.strip()
                    nr += 1
                if read_v80:
                    ll = l.split()
                    if len(ll) == 0:
                        continue
                    self.v80.meas_params[ll[0]] = ll[1]
                if read_con:
                    ll = l.strip().split()
                    if len(ll) == 0:
                        continue
                    if ll[0]=='hutch':
                        if ll[1]=='True':
                            self.condition_hutch = True
                        else:
                            self.condition_hutch = False
                    elif ll[0]=='v80':
                        if ll[1]=='True':
                            self.condition_v80 = True
                        else:
                            self.condition_v80 = False

    def check_conditions(self):
        # more conditions to be added at some stage
        hutchstatus = self.hutch.hutchstatus()
        if type(hutchstatus)==type(None):
            print('hutchstatus type NONE !')
            self.hutchstatus['hutch'] = 'unknown'
            self.hutchstatus['remote'] = 'unknown'
        elif len(hutchstatus) == 0:
            self.hutchstatus['hutch'] = 'unknown'
            self.hutchstatus['remote'] = 'unknown'
        else:
            if 'hutch' in hutchstatus and hutchstatus['hutch'] == '1':
                self.hutchstatus['hutch'] = 'open'
            else:
                self.hutchstatus['hutch'] = 'close'
            if 'remote' in hutchstatus.keys() and hutchstatus['remote'] == '1':
                self.hutchstatus['remote'] = 'remote'
            else:
                self.hutchstatus['remote'] = 'local'

        old = self.conditions_ok
        if self.condition_hutch:
            if len(self.hutchstatus) == 0:
                #return
                self.conditions_ok = True
            if  self.hutchstatus['hutch'].strip() == 'open':
                self.conditions_ok = True
            elif self.hutchstatus['hutch'].strip() == 'unknown':
                self.conditions_ok = True
            else:
                self.conditions_ok = False
            if old != self.conditions_ok:
                logging.warning('Condition changed from %s to %s'%(old,self.conditions_ok))
        else:
            self.conditions_ok = True

    def start_sequence(self):
        self.actual_job = 'run sequence'
        print('Running sequence')
        logging.warning('Set Job to run sequence')

    def stop_sequence(self):
        self.run_seq = False
        print('Stopping sequence')
        #self.motor_park()
        logging.warning('Sequence stopped')

    def terminate_sequence(self):
        self.stop_measure()
        print('Terminating sequence')
        self.actual_job = 'idle'
        self.run_seq = False
        logging.warning('Set Job to run idle')

    def run_sequence(self):
        if not (self.actual_job == 'run sequence'):
            return()
        elif self.run_seq and not self.conditions_ok:
            print('stop sequence')
            self.v80.get_data() # do not save data, because they are very likely not ok
            self.stop_sequence()
            #self.setsr800temp('23.0')
            return()
        elif self.actual_job == 'run sequence' and self.conditions_ok and not self.run_seq:
            self.entry = 1
            self.run_seq = True
            self.v80.get_data() # Remove data from instrument if they exist
        elif not self.run_seq or not self.conditions_ok:
            return()
        nr_entry = len(self.sequence)
        unknown = False # unknown should never become true
        if self.measurement_repeat:
            self.repeat_measure()
        while True:
            # read entry
            command = self.sequence[self.entry].split()
            print(self.entry, self.sequence[self.entry])
            self.entry += 1
            if self.measurement_repeat:
                self.repeat_measure()
            if command[0] == 'reinit':
                if command[1] == 'motor':
                    self.reinitmotor(1)
                else:
                    unknown = True
            elif command[0] == 'set':
                if command[1] == 'sr80':
                    logging.warning('Ignoring: set sr80 temp to '+command[2])
                    #self.setsr80temp(float(command[2]))
                if command[1] == 'sr800':
                    if command[2] == 'on':
                        self.switch_sr800_on()
                    elif command[2] == 'off':
                        self.switch_sr800_off()
                    else:
                        self.setsr800temp(command[2])
                        self.sr800_target_temp = command[2]
                if command[1] == 'motor':
                    #if command[2] == 'sr80':
                    #    self.motor_sr80()
                    #elif command[2] == 'roof':
                    #    self.motor_roof()
                    #elif command[2] == 'park':
                    #    self.motor_park()
                    #else:
                    #    unknown = True
                    self.motor.movetoposition(command[2])
            elif command[0] == 'measure':
                if command[1] == 'start':
                    self.start_measure()
                elif command[1] == 'stop':
                    self.measurement_repeat = False
                    stat = self.v80.get_status()
                    if stat['status'] == 'IDL':
                        self.stop_measure()
                    else:
                        self.entry -= 1
                        break
                elif command[1] == 'repeat':
                    self.measurement_repeat = True
            elif command[0] == 'wait':
                if command[1] == 'sr800':
                    # wait for sr800 to stabilize
                    # self.SR80_stable is set by
                    #self.Temperature_reached()
                    print('waiting for sr800')
                    if not self.sr800.get_stability():
                        print('Waiting for SR800 to reach', self.sr800_target_temp, ' : ', self.sr800.get_temperature())
                        time.sleep(5)
                        self.entry -= 1
                        break
                    else:
                        pass
                elif command[1] == 'time':
                    # Set a timer, goes on only after the time is more than self.time_continue
                    print(dt.datetime.now(), ' -> ', int((self.time_continue-dt.datetime.now()).total_seconds()), 's to go')
                    if dt.datetime.now() < self.time_continue:
                        self.entry -= 1
                        break
                    else:
                        # if a timer has been active, go to next line.
                        # if timer has been set now, go back to this line
                        if self.wait:
                            self.wait = False
                        else:
                            tt = float(command[2])
                            self.time_continue = dt.datetime.now() + dt.timedelta(seconds=tt)
                            self.wait = True
                            self.entry -= 1
            elif command[0] == 'loop':
                self.entry = int(command[1])
            elif command[0] == 'end':
                self.terminate_sequence()
                self.entry = -1
                break
            else:
                unknown = True

    def start_measure(self):
        self.measurement = True
        p = self.motor.position
        if p=='sr800':
            t = '_%03.3f'%(float(self.sr800.get_temperature()))
        elif p=='sr80':
            t = '_%03.3f'%(float(self.sr80.get_temperature()))
        elif p == 'rt':
            t = ''
        elif p=='roof':
            t = ''
        #elif p=='ht':
        #    t = 'seelog'
        else:
            t = '_%03.3f'%(self.preset_temps[p])
        fname = 'nyem'+dt.datetime.now().strftime('%Y%m%d%H%M%S_')+p+t+'.000'
        self.v80.set_sampleform(p+t)
        self.v80.set_samplename(p+t)
        path = os.path.join(self.folder, dt.datetime.now().strftime('%Y%m%d'))
        if not os.path.exists(path):
            os.mkdir(path)
        self.act_filename = os.path.join(path,fname)
        self.v80.measure()
        self.meas_start_time = dt.datetime.now()
#        self.new_measurement = False

    def meas_started(self):
        return(self.meas_start_time)

    def repeat_measure(self):
        stat = self.v80.get_status()
        if stat['status'] == 'IDL':
            self.save_measurement(self.act_filename)
            self.start_measure()

    def stop_measure(self):
        self.measurement = False
        self.save_measurement(self.act_filename)
        pass

    def save_measurement(self,file='Z:\out\tmp\tempspectrum.0'):
        if (self.actual_job == 'run sequence'):
            self.v80.get_data(file)
            self.last_meas_file = file
            print('Recorded interferogram:', self.last_meas_file)
            self.new_measurement = True
            try:
                new_meas = ftsreader(self.last_meas_file)
                self.pka = new_meas.header['Instrument Parameters']['PKA']
            except Exception as e:
                print('Exception in ftsreader call\n',e)
                self.pka = -1

    def get_newmeasurement(self):
        if self.new_measurement:
            return(self.last_meas_file)
        else:
            return(None)

    def motor_park(self):
        self.motor.movetoposition('park')

    def motor_roof(self):
        self.motor.movetoposition('roof')

    def motor_ht(self):
        self.motor.movetoposition('ht')

    def motor_rt(self):
        self.motor.movetoposition('rt')

    def motor_ir301(self):
        self.motor.movetoposition('ir301')

    def motor_sr80(self):
        self.motor.movetoposition('sr80')

    def motor_sr800(self):
        self.motor.movetoposition('sr800')

    def switch_sr800_on(self):
        print('Switching SR800 on')
        self.brennenstuhl.switch_on('1')

    def switch_sr800_off(self):
        print('Switching SR800 off')
        self.brennenstuhl.switch_off('1')

    def switch_ir301_on(self):
        self.brennenstuhl.switch_on('0')

    def switch_ir301_off(self):
        self.brennenstuhl.switch_off('0')

    def initinstruments(self):
        self.sr800 = sr800(addr='172.18.0.140', blockcomm = self.blocksr80comm)
        self.motor = motorctrl(self.motor_com, blockcomm = self.blockmotorcomm)
        self.brennenstuhl = brennenstuhl('172.18.0.150')
        self.v80 = Vertex80()
        self.maxnumber = 1
        self.hutch = hutchsensor(self.hutch_com)


    def setv80param(self):
        l = self.paramtextbox.text().split('|')
        li = [i.split(':')[0].strip() for i in l]
        lj = [i.split(':')[1].strip() for i in l]
        for i,j in zip(li, lj):
            if i in ['AQM']:
                self.v80.meas_params[i] = j.strip()
            elif i in ['RES', 'PHR']:
                self.v80.meas_params[i] = float(j.strip())
            else:
                self.v80.meas_params[i] = int(j.strip())
        for i, j in self.v80.meas_params.items():
            print(i,':',j)

    def sethtparam(self):
        l = self.httextbox.text().strip()
        self.preset_temps['ht'] = float(l)
        print('set ht temp preset to :',l)

    def setir301param(self):
        l = self.ir301textbox.text().strip()
        self.preset_temps['ir301'] = float(l)
        print('set ir301 temp preset to :',l)

    def setsr800temp(self, new_T):
        self.sr800newT = new_T
        self.bbtemp = float(new_T)
        self.sr800.set_temperature(float(new_T))
        print('set sr800 temp to', new_T)
        logging.warning('set sr800 temp to %3.2f'%float(new_T))

    def setsr80temp(self,new_T):
        self.bbtemp = new_T
        print ('setsr80temp',self.bbtemp)
        self.sr80.set_temperature(self.bbtemp)

    def reinitmotor(self, item):
        self.motor.init_motor()

    def getfolder(self):
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        print('Opening ', self.folder)

    def setcheckbox(self, state):
        if state == QtCore.Qt.Checked:
            self.checkbox = True
        else:
            self.checkbox = False

    def Temperature_reached(self):
         pass
    #    t = self.sr80.get_stability()
    #    self.bbstdv = t[1]
    #    if np.abs(t[0] - self.bbtemp) < 0.1 and np.abs(t[1] < 0.1) :
    #        self.SR80_stable = True
    #    else:
    #        self.SR80_stable = False
    #    return(t[0], t[1], self.SR80_stable)
